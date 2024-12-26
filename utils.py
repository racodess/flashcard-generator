import json
import os
import io
import sys
import base64
import argparse

from PIL import Image
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
from rich.markdown import Markdown
from rich.pretty import pprint

from weasyprint import HTML, CSS
import markdown2
import pygments

from rich.console import Console

from templates import ADDITIONAL_CSS

console = Console()

def get_args():
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcards based on input files and Anki tags."
    )
    parser.add_argument(
        'file_path',
        type=str,
        help='Path to the file to process.'
    )
    parser.add_argument(
        'file_name',
        type=str,
        help='Name of the file to process.'
    )
    parser.add_argument(
        'collection_media_path',
        type=str,
        help='Path to the Anki collection.media directory'
    )
    parser.add_argument(
        'tags',
        nargs='*',
        help='Anki tags for the flashcards.'
    )
    parser.add_argument(
        '--code',
        action='store_true',
        help='Indicates that the file is from a problem-solving folder and should be processed with the code flag.'
    )

    return parser.parse_args()


def detect_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.txt':
        return 'text'
    elif ext.lower() == '.pdf':
        return 'pdf'
    elif ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        return 'image'
    else:
        return 'unsupported'


def process_data(file_path, file_type):
    if file_type == 'text':
        with open(file_path, 'r', encoding='utf-8') as f:
            plain_text = f.read()
        return plain_text

    if file_type == 'image':
        img = Image.open(file_path)
        img_uri = get_img_uri(img)
        return img_uri

    if file_type == 'pdf':
        images = convert_doc_to_images(file_path)
        img_uri = get_img_uri(images[0])
        return img_uri

    console.print(
        f"Unsupported file type: '{file_path}'.\n"
        "Supported file types are '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp'",
        style="red"
    )
    sys.exit(1)


def convert_doc_to_images(path):
    images = convert_from_path(path)
    return images


def extract_text_from_doc(path):
    return extract_text(path)


def get_img_uri(img):
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_png}"


def create_pdf_from_markdown(collection_media_path, file_name, text_markdown):
    pdf_folder = os.path.join(collection_media_path, "_pdf_files")
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, f"{file_name}.pdf")

    html_content = markdown2.markdown(
        text_markdown,
        extras=[
            "fenced-code-blocks",
            "highlight_code",
            "code-friendly",
        ]
    )

    additional_css = ADDITIONAL_CSS

    try:
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=additional_css)]
        )
        print(f"PDF created successfully at: {pdf_path}")
    except Exception as e:
        print(f"Failed to create PDF from txt file: {e}")


def parse_llm_response(response_str):
    try:
        data = json.loads(response_str)

        concepts = data.get("concepts", [])

        return concepts

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in parse_llm_response method: {e}")

        return [], []


def print_message(role, content, response_format, model, markdown):
    role_styles = {
        "system": "[bold cyan]System Message",
        "user": "[bold green]User Message",
        "assistant": f"[bold yellow]{model}: Response",
        "token": "[bold magenta]Token Usage",
        "flashcard": "[bold orange]Flashcards",
    }

    rule = role_styles.get(role.lower(), f"[bold]{role} Message")
    console.rule(rule)

    if markdown and isinstance(content, str):
        console.print("\n", Markdown(content), "\n")
        return

    if role.lower() == "token":
        print("\n")
        pprint(content, expand_all=True)
        print("\n")
        return

    if role.lower() == "assistant":
        text_content = response_format.model_validate_json(content)
        pprint(text_content)
        return

    if role.lower() == "flashcard":
        pprint(content)
        return

    console.print("\n", content, "\n")


def append_message(role, response, messages):
    message = {"role": role.lower(), "content": response}
    messages.append(message)