"""
Purpose:

- Formatting utilities:
    - Generating PDF from information plain text .txt files that DO NOT contain URLs
    - Parsing list of concepts required in flashcard generation pipeline
    - Printing messages
"""
import os
import json

from rich.markdown import Markdown
from rich.pretty import pprint
from rich.console import Console

import markdown2
from weasyprint import HTML, CSS
# used by weasyprint
import pygments

from utils.flashcard_logger import logger
from utils.templates import ADDITIONAL_CSS

console = Console()


def fill_data_fields(flashcard_obj, url_name, source_name, content_type):
    """
    - Adds extra metadata fields to each flashcard as required by the Anki add-on "pdf viewer and editor".
    """
    for fc in flashcard_obj.flashcards:
        fc.data.image = source_name if content_type == "image" else ""
        fc.data.external_source = source_name if content_type != "image" else ""
        fc.data.external_page = 1
        fc.data.url = url_name


def create_pdf_from_markdown(collection_media_path: str, file_name: str, text_markdown: str) -> None:
    """
    - For generating high-quality PDFs (currently from a concept map prompt) from plain text .txt files that DO NOT contain URLs.
    - Uses `markdown2` to convert Markdown text to HTML, then calls WeasyPrint to create a clean and colorful PDFs featuring syntax highlighting for code.
    - Stores the resulting PDF inside `_pdf_files` in Anki’s media folder to be used as a source file linked within flashcards; requires a separate Anki add-on "pdf viewer and editor".
    """
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

    try:
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=ADDITIONAL_CSS)]
        )
        logger.info("PDF created successfully at: %s", pdf_path)
    except Exception as e:
        logger.error("Failed to create PDF from %s: %s", file_name, e)


def parse_concepts_list_response(response_str: str):
    """
    - Tries to `json.loads(...)` the string, returns a list of concepts if they exist.
    - Uses a `try/except` block to handle `json.JSONDecodeError`.
    """
    try:
        data = json.loads(response_str)
        return data.get("concepts", [])
    except json.JSONDecodeError as e:
        logger.error("Error parsing JSON in parse_concepts_list_response: %s", e)
        return []


def print_message(role, content, response_format, model, markdown):
    """
    - Uses `rich.console.Console` and the `Markdown` object to do pretty printing.
    - If `markdown=True`, it will render the content as Markdown.
    - If the role is "assistant" and `response_format` can parse the content, it tries to do so. Otherwise, it just prints.
    """
    role_styles = {
        "system": "[bold cyan]System Message",
        "user": "[bold green]User Message",
        "assistant": f"[bold yellow]{model}: Response" if model else "[bold yellow]Assistant",
        "token": "[bold magenta]Token Usage",
        "concept_flashcards": "[bold orange]Concept Flashcards",
        "problem_flashcards": "[bold red]Problem Flashcards",
    }

    # If content is Markdown text
    if markdown and isinstance(content, str):
        console.print("\n", Markdown(content), "\n")
        return

    # Token usage
    if role.lower() == "token":
        print("\n")
        pprint(content, expand_all=True)
        print("\n")
        return

    # If role is 'assistant' with a possible JSON content
    if role.lower() in ["assistant"]:
        if hasattr(response_format, "model_validate_json") and isinstance(content, str):
            try:
                text_content = response_format.model_validate_json(content)
                pprint(text_content)
                return
            except Exception:
                console.print("\n", content, "\n")
                return
        console.print("\n", content, "\n")
        return

    # For 'flashcard' or 'problem_flashcards', just pprint
    if role.lower() in ["concept_flashcards", "problem_flashcards"]:
        console.rule("Completed Flashcards")

        pprint(content, expand_all=True)
        return

    # Default
    console.print("\n", content, "\n")
