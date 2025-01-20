"""
Formatting utilities:
- Generating PDF from information plain text .txt files that DO NOT contain URLs
- Parsing list of concepts required in flashcard generation pipeline
- Printing messages
"""
import os

from rich.pretty import pprint
from rich.console import Console

import markdown2
from weasyprint import HTML, CSS
# used by weasyprint

from utils.flashcard_logger import logger
from utils.templates import ADDITIONAL_CSS

console = Console()


def set_data_fields(
        card_model,
        url_name,
        file_name,
        content_type
):
    for fc in card_model.flashcards:
        fc.data.image = file_name if content_type == "image" else ""
        fc.data.external_source = file_name if content_type != "image" else ""
        fc.data.external_page = 1
        fc.data.url = url_name


def make_pdf(
        media_path: str,
        file_name: str,
        text: str
) -> None:
    """
    - For generating high-quality PDFs (currently from a concept map prompt) from plain text .txt files that DO NOT contain URLs.
    - Uses `markdown2` to convert Markdown text to HTML, then calls WeasyPrint to create a clean and colorful PDFs featuring syntax highlighting for code.
    - Stores the resulting PDF inside `_pdf_files` in Anki’s media folder to be used as a source file linked within flashcards; requires a separate Anki add-on "pdf viewer and editor".
    """
    pdf_folder = os.path.join(media_path, "_pdf_files")
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, f"{file_name}.pdf")

    html_content = markdown2.markdown(
        text,
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


def print_flashcards(content):
    console.rule("Completed Flashcards")
    pprint(content, expand_all=True)
