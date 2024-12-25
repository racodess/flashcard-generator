import os
import io
import re
import sys
import json
import base64
import argparse

from PIL import Image
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text

from rich.console import Console
from rich.markdown import Markdown
from rich.pretty import Pretty, pprint

from weasyprint import HTML, CSS
import markdown2
import pygments


from openai import OpenAI

from importer import add_flashcards_to_anki
from models import Concepts, Flashcard, ValidationError, ProblemFlashcard
from prompts import (
    TEXT_FORMAT,
    PLACEHOLDER_MESSAGE,
    CONCEPT_MAP_PROMPT,
    DRAFT_FLASHCARD_PROMPT,
    FINAL_FLASHCARD_PROMPT,
    PROBLEM_FLASHCARD_PROMPT,
    CONCEPTS_LIST_PROMPT,
    ABSENT_PROMPT,
)

# OpenAI Models
GPT_O1_PREVIEW = "o1-preview"
GPT_O1_MINI = "o1-mini"
GPT_4O = "gpt-4o-2024-11-20"
GPT_4O_MINI = "gpt-4o-mini"

client = OpenAI()

console = Console()

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


def process_file(file_path, file_type):
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


def get_completion(file_type, model, message_list, response_format):
    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=message_list,
            response_format=response_format,
            max_completion_tokens=16384,
            temperature=0,
            top_p=0.1,
        )
        finish_reason = completion.choices[0].finish_reason
        if finish_reason != "stop":
            console.rule("[bold yellow] Finish Reason")
            console.print(
                f"Finished processing {file_type} with reason: {finish_reason}",
                style="yellow"
            )
        return completion
    except Exception as e:
        console.print(f"Error in processing {file_type}: ", Pretty(e, expand_all=True), style="red")
        sys.exit(1)



def handle_completion(system_message, user_message, response_format, file_type, run_as_image=False):
    message_list = [{"role": "system", "content": system_message}]

    print_message("system", system_message, response_format, model=None, markdown=True)

    if run_as_image:
        model = GPT_4O
        content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{user_message}"
                }
            }
        ]
        append_message("user", content, message_list)
        print_message("user", PLACEHOLDER_MESSAGE, response_format, model=None, markdown=True)
    else:
        model = GPT_4O_MINI
        append_message("user", user_message, message_list)
        print_message("user", user_message, response_format, model=None, markdown=True)

    completion = get_completion(
        file_type,
        model=model,
        message_list=message_list,
        response_format=response_format,
    )

    print_message("token", completion.usage, response_format, model=None, markdown=False)
    model = completion.model
    response = completion.choices[0].message.content

    if response_format is TEXT_FORMAT:
        print_message("assistant", response, response_format, model, markdown=True)
    else:
        print_message("assistant", response, response_format, model, markdown=False)

    return response


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

    additional_css = """
    @page {
        size: Letter;
        margin: 0.25in;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 20px;
    }
    th, td {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    body {
        font-family: Arial, sans-serif;
        line-height: 1.5;
        color: #2c3e50;
        margin: 0; /* We rely on @page margin for PDF */
    }
    p {
        margin: 0 0 1em 0;
    }
    ul, ol {
        margin: 0 0 1em 1.5em;
        padding: 0;
        list-style-position: outside;
    }
    li {
        margin-bottom: 0.5em;
    }
    strong {
        font-weight: bold;
        font-size: 1.1em;
    }
    div.codehilite, pre {
        background-color: #272822; 
        color: #f8f8f2;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
        margin: 1em 0;
        font-family: Consolas, "Courier New", Courier, monospace;
        font-size: 0.9em;
        line-height: 1.4;
    }
    div.codehilite code, pre code {
        background: none;  /* Let the parent div handle background */
        color: inherit;
        font-family: inherit;
        font-size: inherit;
        line-height: inherit;
    }
    /* Pygments token classes you may see in the snippet:
       .n (names), .nf (function names), .k (keywords),
       .kd (keyword declarations), .kt (data types), .c1 (comments),
       .mi (numbers), .err (lexing errors), etc.
    */
    .n  { color: #a8b3ab; }     /* Generic text/name */
    .nf { color: #66d9ef; }     /* Function name */
    .k  { color: #66d9ef; }     /* Keyword */
    .kd { color: #66d9ef; }     /* Keyword declaration (e.g., 'public', 'class') */
    .kt { color: #fd971f; }     /* Data type keywords (e.g., int, float) */
    .c1 { color: #75715e; font-style: italic; }  /* Comment */
    .mi { color: #ae81ff; }     /* Number (int, float literals) */
    .err { color: #ff0000; }    /* Anything flagged as an error token */
    code {
        background-color: #f5f5f5;
        color: #c7254e;
        font-family: Consolas, "Courier New", Courier, monospace;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    """

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


def main():
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

    args = parser.parse_args()
    file_path = args.file_path
    file_name = args.file_name
    collection_media_path = args.collection_media_path
    tags = args.tags
    is_code = args.code

    file_type = detect_file_type(
        file_path
    )
    file_contents = process_file(
        file_path,
        file_type
    )

    console.print(
        f"\nProcessing path: {file_path}"
    )
    console.print(
        f"\nProcessing file: {file_name}"
    )
    console.print(
        f"\nTags: \n{tags}"
    )

    # TODO: import to new decks
    # TODO: html error in markdown code for Java generics
    # TODO: reorganize code

    if is_code:
        problem_flashcard_prompt = PROBLEM_FLASHCARD_PROMPT.format(
            tags=tags
        )
        problem_flashcard_response = handle_completion(
            problem_flashcard_prompt,
            file_contents,
            ProblemFlashcard,
            file_type,
            run_as_image=True
        )
        problem_flashcard_model = ProblemFlashcard.model_validate_json(
            problem_flashcard_response
        )

        for fc in problem_flashcard_model.flashcards:
            fc.image = file_name if file_type == "image" else ""
            fc.external_source = file_name if file_type != "image" else ""
            fc.external_page = 1

        print_message(
            "problem_flashcards",
            problem_flashcard_model,
            response_format=None,
            model=None,
            markdown=False
        )

        add_flashcards_to_anki(
            problem_flashcard_model,
            template_name="AnkiConnect: Problem",
            deck_name="TestAnkiConnect"
        )
    else:
        concept_map_response = handle_completion(
            CONCEPT_MAP_PROMPT,
            file_contents,
            TEXT_FORMAT,
            file_type,
            run_as_image=True
        )
        draft_concepts_list_prompt = CONCEPTS_LIST_PROMPT.format(
            tags=tags
        )
        draft_concepts_list_response = handle_completion(
            draft_concepts_list_prompt,
            concept_map_response,
            Concepts,
            file_type
        )
        absent_prompt = ABSENT_PROMPT.format(
            tags=tags,
            source_material=concept_map_response
        )
        final_concepts_list_response = handle_completion(
            absent_prompt,
            draft_concepts_list_response,
            Concepts,
            file_type
        )
        concepts_list = parse_llm_response(
            final_concepts_list_response
        )
        draft_flashcard_response = handle_completion(
            DRAFT_FLASHCARD_PROMPT,
            f"""
            #### list of each concept item to be addressed, along with the relevant additional information for each item:
            {concepts_list}
            """,
            Flashcard,
            file_type
        )
        final_flashcard_response = handle_completion(
            FINAL_FLASHCARD_PROMPT,
            f"""
            #### List of each concept item to be addressed, along with the relevant additional information for each item:
            {concepts_list}
            ------
            #### The first draft of flashcards created from the list of concepts:
            {draft_flashcard_response}
            """,
            Flashcard,
            file_type
        )
        try:
            flashcard_model = Flashcard.model_validate_json(
                final_flashcard_response
            )
        except ValidationError as e:
            console.print(
                "Error parsing concept_flashcards:",
                style="red"
            )
            console.print(
                str(e),
                style="red"
            )
            sys.exit(1)

        for fc in flashcard_model.flashcards:
            fc.title = flashcard_model.title
            fc.front = fc.content.front
            fc.back = fc.content.back
            fc.image = file_name if file_type == "image" else ""
            fc.external_source = file_name if file_type != "image" else ""
            fc.external_page = 1

        print_message(
            "flashcard",
            flashcard_model.flashcards,
            response_format=None,
            model=None,
            markdown=False
        )

        if file_type.lower() == "text":
            create_pdf_from_markdown(
                collection_media_path,
                file_name,
                concept_map_response
            )

        add_flashcards_to_anki(
            flashcard_model,
            template_name="AnkiConnect: Test",
            deck_name="TestAnkiConnect"
        )


if __name__ == "__main__":
    main()