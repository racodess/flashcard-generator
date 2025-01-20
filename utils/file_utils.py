"""
File utilities:
- Determining file type from the extension
- Reading the file content accordingly: text, JSON, images, PDF
- Converting PDFs to images (using `pdf2image.convert_from_path`)
- Base64 encoding of Images as required by the OpenAI API
- Handling unsupported file types with a custom `UnsupportedFileTypeError`
"""
import os
import io
import json
import yaml
import base64
from PIL import Image

from rich.console import Console

from pdf2image import convert_from_path
from pdfminer.high_level import extract_text

from utils.flashcard_logger import logger

class UnsupportedFileTypeError(Exception):
    """Raised when encountering an unsupported file type."""

console = Console()

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


def get_data(file_path: str, content_type: str):
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


def get_tags(directory):
    """
    Reads a metadata.yaml file in the given directory, parses the 'tags' section,
    and returns a list of strings. If metadata.yaml or 'tags:' is missing, returns [].
    """
    yaml_data = _get_metadata(directory)

    if "anki_tags" not in yaml_data:
        logger.warning("No 'anki_tags:' key found in metadata.yaml in %s. Proceeding without Anki tags.", directory)
        return []

    tags_section = yaml_data["anki_tags"]

    # Now recursively flatten that structure:
    flattened_tags = _flatten_tags(tags_section, [])

    # Log local tags for debugging
    console.log("[bold red] Local tags:", flattened_tags)

    return flattened_tags


def get_ignore_list(directory):
    """
    Reads the 'ignore' list from metadata.yaml and returns a list of headings to ignore.
    If 'ignore:' is missing, returns an empty list.
    """
    yaml_data = _get_metadata(directory)

    if "ignore_sections" not in yaml_data:
        logger.warning("No 'ignore_sections:' key found in metadata.yaml in %s. Proceeding with all extracted sections.", directory)
        return []

    ignore_headings = yaml_data["ignore_sections"]

    if not isinstance(ignore_headings, list):
        logger.warning("'ignore_heading:' should be a list in metadata.yaml. Found type '%s'.", type(ignore_headings))
        return []

    # Log list of ignored headings for debugging
    console.log("[bold red] Ignoring headings:", ignore_headings)

    return ignore_headings


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


def _flatten_tags(obj, path_so_far):
    """
    Recursively walk a nested dict-or-list structure of tags
    and produce flattened '::'-separated paths, e.g.:
      - "Python"
      - "Python::Basics"
      - "Python::Basics::Syntax"
    """
    results = []

    # Case 1: obj is a dictionary
    if isinstance(obj, dict):
        for key, val in obj.items():
            # Immediately add the key itself as a "leaf" (e.g. "Python", "Python::Basics", ...)
            new_path = path_so_far + [str(key)]
            results.append("::".join(new_path))

            # Then handle children
            if isinstance(val, dict):
                # Recurse deeper
                results.extend(_flatten_tags(val, new_path))
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        results.extend(_flatten_tags(item, new_path))
                    else:
                        # item is a leaf string => e.g. "Syntax"
                        results.append("::".join(new_path + [str(item)]))
            else:
                # val is a direct leaf
                results.append("::".join(new_path + [str(val)]))

    # Case 2: obj is a list
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_flatten_tags(item, path_so_far))

    # Case 3: obj is a scalar (string, int, etc.)
    else:
        # Just a direct leaf
        results.append("::".join(path_so_far + [str(obj)]))

    return results


def _get_metadata(directory):
    """
    Expecting something like:

    ```yaml
    tags:
      - Python:
        - Basics:
          - Syntax
          - Data_Types
        - Functions:
          - Defining
          - Lambda

    ignore:
        - Exercises
        - Summary
    ```
    """
    metadata_file = os.path.join(directory, "metadata.yaml")
    if not os.path.isfile(metadata_file):
        logger.warning("No metadata.yaml found in %s.", directory)
        return []

    with open(metadata_file, 'r', encoding='utf-8') as f:
        try:
            yaml_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error("Error parsing metadata.yaml in %s: %s", directory, e)
            return []

    return yaml_data


def _get_image(path: str):
    """
    - Convert PDF into a list of images (one per page).
    - Currently the application intentionally supports only a one-page PDF by creating an image from the first page.
    """
    return convert_from_path(path)


def _get_pdf_text(path: str) -> str:
    """
    - Extract text from a PDF via pdfminer.
    - Currently all PDFs are intentionally handled as images.
    """
    return extract_text(path)


def _get_img_uri(img: Image.Image) -> str:
    """
    - Takes a PIL Image, writes it to an in-memory buffer as PNG, base64-encodes it, and returns the base64 string.
    - This is used by `file_utils` to handle images.
    """
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_png}"


def _get_plain_text(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _read_image_file(file_path: str) -> str:
    img = Image.open(file_path)
    return _get_img_uri(img)


def _read_pdf_file(file_path: str) -> str:
    images = _get_image(file_path)
    if images:
        return _get_img_uri(images[0])
    return ""

READ_DISPATCH = {
    'text': _get_plain_text,
    'image': _read_image_file,
    'pdf': _read_pdf_file
}
