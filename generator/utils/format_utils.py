"""
Purpose:

- Formatting and conversion utilities.
"""
import os
import io
import base64
from PIL import Image

import markdown2
from weasyprint import HTML, CSS

# used by weasyprint
import pygments

from flashcard_logger import logger
from templates import ADDITIONAL_CSS


def get_img_uri(img: Image.Image) -> str:
    """
    - Takes a PIL Image, writes it to an in-memory buffer as PNG, base64-encodes it, and returns the `data:image/png;base64,<...>` string.
    - This is used by `file_utils` to handle images.
    """
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return base64_png


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
