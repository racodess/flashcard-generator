"""
Purpose:

- Determining file type from the extension,
- Reading the file content accordingly: text, JSON, images, PDF,
- Converting PDFs to images (using `pdf2image.convert_from_path`),
- Handling unsupported file types with a custom `UnsupportedFileTypeError`.
"""
import os
import json
from PIL import Image

# TODO: Currently handles all PDFs (intentional)
from pdf2image import convert_from_path

# TODO: Currently unused (intentional)
from pdfminer.high_level import extract_text

from generator.utils.flashcard_logger import logger
from generator.utils import format_utils

class UnsupportedFileTypeError(Exception):
    """Raised when encountering an unsupported file type."""

# A dict mapping file extensions to a broad "content type".
EXTENSION_CONTENT_TYPE_MAP = {
    '.txt': 'text',
    '.pdf': 'pdf',
    '.json': 'json',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.gif': 'image',
    '.bmp': 'image',
}


# TODO: Subject to change; There is no special flow to handle JSON data (beyond reading it), Multi-page PDFs (only the first page), Video/Audio or any other formats
def get_content_type(file_path: str, url: str = None) -> str:
    """
    - If `url` is provided, returns `'url'`;
    - Else extracts file extension and returns `'unsupported'` if it’s not recognized.
    """
    if url:
        return 'url'
    if file_path:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        return EXTENSION_CONTENT_TYPE_MAP.get(ext, 'unsupported')
    return 'unsupported'


def process_data(file_path: str, content_type: str):
    """
    - Looks up the appropriate function in `READ_DISPATCH` and returns its result.
    - Raises a custom `UnsupportedFileTypeError` exception if content type is unsupported.
    """
    read_func = READ_DISPATCH.get(content_type)
    if not read_func:
        raise UnsupportedFileTypeError(f"Unsupported file type: {content_type}")

    try:
        return read_func(file_path)
    except Exception as e:
        logger.error("Error processing file %s as %s: %s", file_path, content_type, e)
        raise


"""
Reader Functions:

- `read_text_file(...)` – opens the file, returns the text.
- `read_json_file(...)` – deserializes JSON to a Python object.
- `read_image_file(...)` – returns a base64-encoded image URI required by the OpenAI completions API.
- `read_pdf_file(...)` – converts the first PDF page into a base64 PNG image.
"""
def read_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_json_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_image_file(file_path: str) -> str:
    img = Image.open(file_path)
    return format_utils.get_img_uri(img)


def read_pdf_file(file_path: str) -> str:
    images = convert_doc_to_images(file_path)
    if images:
        return format_utils.get_img_uri(images[0])
    return ""


# TODO: Currently handles all PDFs (intentional)
# TODO: Implement document segmentation using Aryn
def convert_doc_to_images(path: str):
    """
    - Convert PDF into a list of images (one per page).
    - Currently the application intentionally supports only a one-page PDF by creating an image from the first page.
    """
    return convert_from_path(path)


# TODO: Currently unused (intentional)
# TODO: Implement document segmentation using Aryn
def extract_text_from_doc(path: str) -> str:
    """
    - Extract text from a PDF via pdfminer.
    - Currently all PDFs are intentionally handled as images.
    """
    return extract_text(path)

"""
- A dict that maps `'text'`, `'json'`, `'image'`, and `'pdf'` to specific reader functions.  
- This design is a dispatcher pattern, where you pick a function based on a “content type” key.
"""
READ_DISPATCH = {
    'text': read_text_file,
    'json': read_json_file,
    'image': read_image_file,
    'pdf': read_pdf_file
}
