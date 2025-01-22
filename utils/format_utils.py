"""
Formatting utilities for flashcards and text documents.

This module provides functions for:
1. Generating PDFs from plain text or Markdown-like content (via `weasyprint` and `markdown2`).
2. Setting extra fields (metadata) on flashcards before import.
3. Printing flashcards in a structured manner to the console.

Usage context:
  - Typically called after text or URL content is retrieved and segmented.
  - PDFs can be automatically generated for reference material (e.g., concept maps).
"""
import os

from rich.pretty import pprint
from rich.console import Console

import markdown2
from weasyprint import HTML, CSS

from utils.flashcard_logger import logger
from utils.templates import ADDITIONAL_CSS

console = Console()


def set_data_fields(
        card_model,
        url_name,
        file_name,
        content_type
):
    """
    Populates certain metadata fields in each flashcard within `card_model`.

    Logic:
      - If it's an image file, store the `file_name` in the 'image' field.
      - Otherwise, store the `file_name` as an 'external_source'.
      - Set 'external_page' to 1 by default (useful if referencing multi-page PDFs).
      - Attach the `url_name` (if any) so the flashcard can link back to the source.

    Args:
        card_model (BaseModel): A flashcard model with a `.flashcards` list.
        url_name (str): The URL (if relevant) to associate with the flashcards.
        file_name (str): The original filename (for reference).
        content_type (str): The type of content ("image", "pdf", "text", etc.).
    """
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
    Creates a PDF from given text (often Markdown) and saves it into Anki's
    media folder under `_pdf_files`.

    Steps:
      1. Convert the provided `text` to HTML using `markdown2` with extras:
         - "fenced-code-blocks" for triple-backtick code formatting.
         - "highlight_code" for syntax highlighting.
         - "code-friendly" for better code block handling.
      2. Use `WeasyPrint` to render the HTML as a PDF.
      3. Save the resulting PDF within `_pdf_files` under the `media_path`.

    This PDF can be referenced in Anki flashcards (requires a PDF-friendly add-on).

    Args:
        media_path (str): The path to Anki's media folder (e.g., `collection.media`).
        file_name (str): Name to give the resulting PDF (without `.pdf` extension).
        text (str): The raw text content (potentially Markdown) to convert into a PDF.

    Raises:
        Exception: If the PDF generation fails for any reason.
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
    """
    Prints structured flashcard content to the console for debugging/inspection.

    Args:
        content (Any): The flashcard data (or a list of flashcards) to display.
    """
    console.rule("Completed Flashcards")
    pprint(content, expand_all=True)
