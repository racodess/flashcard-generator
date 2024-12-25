import os
import io
import sys
import shutil
import base64
import argparse
import subprocess

from PIL import Image
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text

from weasyprint import HTML, CSS
import markdown2
import pygments

from rich.console import Console
from rich import print as rprint

from templates import ADDITIONAL_CSS

console = Console()

processed_any_files = False  # Global flag to track if any files were processed.

def determine_collection_media_path():
    if sys.platform.startswith('win'):
        return os.path.expandvars(r'%APPDATA%\Anki2\User 1\collection.media')
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser('~/Library/Application Support/Anki2/User 1/collection.media')
    else:
        return os.path.expanduser('~/Documents/Anki2/User 1/collection.media')


def process_file(file_path, used_dir, tags):
    global processed_any_files

    base_dir = os.path.dirname(file_path)
    rel_path = os.path.relpath(base_dir, DIRECTORY_PATH)
    if rel_path == '.':
        rel_path = ''

    target_dir = os.path.join(used_dir, rel_path)
    os.makedirs(target_dir, exist_ok=True)

    new_file_path = os.path.join(target_dir, os.path.basename(file_path))
    shutil.move(file_path, new_file_path)

    collection_media_path = determine_collection_media_path()
    os.makedirs(collection_media_path, exist_ok=True)

    file_ext = os.path.splitext(new_file_path)[1].lower()
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        shutil.copy2(new_file_path, collection_media_path)
    elif file_ext == '.pdf':
        pdf_dir = os.path.join(collection_media_path, '_pdf_files')
        os.makedirs(pdf_dir, exist_ok=True)
        shutil.copy2(new_file_path, pdf_dir)
    else:
        shutil.copy2(new_file_path, collection_media_path)

    is_problem_solving = 'problem_solving' in os.path.normpath(rel_path).split(os.sep)

    command = [sys.executable, 'generator.py', new_file_path, os.path.basename(new_file_path), collection_media_path] + tags

    if is_problem_solving:
        command.append('--code')

    subprocess.run(command)

    processed_any_files = True


tags = []
def process_directory_recursive(current_directory, used_dir):
    if os.path.basename(current_directory) == "used-files":
        return

    try:
        entries = os.listdir(current_directory)
    except PermissionError:
        rprint(f"[yellow]Warning: Permission denied for directory {current_directory}. Skipping.[/yellow]")
        return

    entries_full_paths = [os.path.join(current_directory, e) for e in entries]

    files = [f for f in entries_full_paths if os.path.isfile(f)]
    subdirs = [d for d in entries_full_paths if os.path.isdir(d)]

    tags_file = os.path.join(current_directory, "tags.txt")
    tags_exist = False
    if os.path.isfile(tags_file):
        tags_exist = True
        # Read tags
        with open(tags_file, 'r', encoding='utf-8') as tf:
            tags = [line.strip() for line in tf if line.strip()]

    files_to_process = [f for f in files if os.path.basename(f) != "tags.txt"]

    if files_to_process:
        if not tags_exist:
            rprint(f"[yellow]Warning: No tags.txt found in {current_directory}. Proceeding without flashcard tags. Your flashcards will be imported to Anki without tags.[/yellow]")
        for f in files_to_process:
            process_file(f, used_dir, tags)

    for sd in subdirs:
        if os.path.basename(sd) == "used-files":
            continue
        process_directory_recursive(sd, used_dir)


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

    print(text_markdown)

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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python processor.py <directory_path>")
        sys.exit(1)

    DIRECTORY_PATH = sys.argv[1]

    if not os.path.isdir(DIRECTORY_PATH):
        print(f"The provided path is not a directory: {DIRECTORY_PATH}")
        sys.exit(1)

    used_dir = os.path.join(DIRECTORY_PATH, "used-files")
    if not os.path.exists(used_dir):
        os.makedirs(used_dir)

    process_directory_recursive(DIRECTORY_PATH, used_dir)

    if not processed_any_files:
        rprint("[red]Error: No files found to process.[/red]")