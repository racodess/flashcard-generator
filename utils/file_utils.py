"""
File utilities module that provides helper functions for:

1. Determining the file type from its extension (e.g., '.txt', '.pdf', '.png').
2. Reading file content and converting it to a format usable by the rest of the code:
   - Plain text reading (.txt).
   - Extracting text from PDF (.pdf) or converting the PDF to a single image.
   - Reading image files (.png, .jpg, etc.) and converting them to a base64-encoded string.
3. Handling YAML-based metadata, including:
   - 'anki_tags' for tagging flashcards.
   - 'ignore_sections' for ignoring certain headings.
4. Providing a centralized dispatch mechanism (READ_DISPATCH) to handle each content type.
5. Defining and raising a custom `UnsupportedFileTypeError` when encountering unknown file types.

Dependencies/Tools:
    - `pdf2image.convert_from_path`: Converts PDFs to one or more PIL images.
    - `pdfminer.high_level.extract_text`: Extracts textual content from PDFs.
    - `PIL` (Pillow) for reading image files.
    - `base64` encoding for converting images to data URIs.
    - `yaml` for loading and parsing metadata (metadata.yaml).
"""
import os
import io
import yaml
import base64
from PIL import Image

from rich.console import Console

from pdf2image import convert_from_path
from pdfminer.high_level import extract_text

from utils.flashcard_logger import logger


class UnsupportedFileTypeError(Exception):
    """
    Custom exception raised when an unsupported file type is encountered.
    For example, if a file's extension is not in EXTENSION_CONTENT_TYPE_MAP
    or if no read function is found in READ_DISPATCH.
    """
    pass


console = Console()

# Maps common file extensions to a broad content type understood by the system.
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
    Retrieves the content of a file based on the assigned `content_type`.

    Steps:
      1. Looks up the corresponding read function in `READ_DISPATCH`.
      2. If no matching function is found, raises `UnsupportedFileTypeError`.
      3. Invokes the read function on `file_path`.

    Args:
        file_path (str): The full path to the file.
        content_type (str): One of 'text', 'pdf', 'image', etc. Must exist in READ_DISPATCH.

    Returns:
        Varies by content_type:
            - 'text': returns a string of the file’s contents.
            - 'image' or 'pdf': returns a base64-encoded data URI string (for the first page if PDF).
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
    Reads the list of flashcard tags from `metadata.yaml` under the key 'anki_tags'.
    The tags may be structured as nested dictionaries or lists, which get flattened
    into double-colon-separated strings (e.g., "Python::Basics::Syntax").

    If `metadata.yaml` is missing or the `anki_tags` key is not found, returns an empty list.

    Args:
        directory (str): The directory path where `metadata.yaml` is located.

    Returns:
        list of str: Flattened, namespace-like tags.
    """
    yaml_data = _get_metadata(directory)

    if "anki_tags" not in yaml_data:
        logger.warning("No 'anki_tags:' key found in metadata.yaml in %s. Proceeding without Anki tags.", directory)
        return []

    tags_section = yaml_data["anki_tags"]

    # Recursively flatten the YAML structure into a list of string tags
    flattened_tags = _flatten_tags(tags_section, [])

    # Log the discovered tags
    console.log("[bold red] Local tags:", flattened_tags)

    return flattened_tags


def get_ignore_list(directory):
    """
    Reads a list of headings to ignore from `metadata.yaml` under the key 'ignore_sections'.
    These headings can then be used to skip certain sections while processing a text (like a webpage).

    If `metadata.yaml` is missing or no `ignore_sections` key is found, returns an empty list.

    Args:
        directory (str): The directory path where `metadata.yaml` is located.

    Returns:
        list of str: A list of headings to ignore.
    """
    yaml_data = _get_metadata(directory)

    if "ignore_sections" not in yaml_data:
        logger.warning("No 'ignore_sections:' key found in metadata.yaml in %s. Proceeding with all extracted sections.", directory)
        return []

    ignore_headings = yaml_data["ignore_sections"]

    if not isinstance(ignore_headings, list):
        logger.warning("'ignore_heading:' should be a list in metadata.yaml. Found type '%s'.", type(ignore_headings))
        return []

    # Log which sections will be ignored
    console.log("[bold red] Ignoring headings:", ignore_headings)

    return ignore_headings


def get_content_type(file_path: str, url: str = None) -> str:
    """
    Determines the content type based on either the presence of a URL or a file extension.

    Logic:
      - If `url` is provided, return 'url' immediately.
      - Otherwise, split the file extension from `file_path` and match it in EXTENSION_CONTENT_TYPE_MAP.
      - Defaults to 'unsupported' if none matches.

    Args:
        file_path (str): The file path to inspect.
        url (str, optional): If provided, indicates that the content source is a URL.

    Returns:
        str: 'url', 'text', 'pdf', 'image', or 'unsupported'.
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
    Recursively transforms a nested structure (dicts/lists) into a list of double-colon
    separated strings representing hierarchical tag paths.

    Example of usage:
      If the YAML data for tags is:
        {
          "Python": {
             "Basics": ["Syntax", "Data_Types"]
          }
        }
      This returns:
        [
          "Python",
          "Python::Basics",
          "Python::Basics::Syntax",
          "Python::Basics::Data_Types"
        ]

    Args:
        obj (any): A dict, list, or scalar (string, int, etc.).
        path_so_far (list): A list of parent keys used to build the hierarchical path.

    Returns:
        list of str: Flattened tag strings.
    """
    results = []

    # If obj is a dict, each key becomes part of the path
    if isinstance(obj, dict):
        for key, val in obj.items():
            new_path = path_so_far + [str(key)]
            # The key itself is a "heading" tag
            results.append("::".join(new_path))

            # Then descend into its value
            if isinstance(val, dict):
                # Recurse further
                results.extend(_flatten_tags(val, new_path))
            elif isinstance(val, list):
                # If it's a list, handle each item in that list
                for item in val:
                    if isinstance(item, dict):
                        # Recurse into nested dict
                        results.extend(_flatten_tags(item, new_path))
                    else:
                        # It's a leaf item, e.g., "Syntax"
                        results.append("::".join(new_path + [str(item)]))
            else:
                # val is a direct scalar leaf
                results.append("::".join(new_path + [str(val)]))

    # If obj is a list, handle each element
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_flatten_tags(item, path_so_far))

    # If obj is a scalar, just append it to the path
    else:
        results.append("::".join(path_so_far + [str(obj)]))

    return results


def _get_metadata(directory):
    """
    Internal helper to load and parse `metadata.yaml` in the given directory.

    Example structure:

    ```yaml
    anki_tags:
      - Python:
        - Basics:
          - Syntax
          - Data_Types
        - Functions:
          - Defining
          - Lambda

    ignore_sections:
      - Exercises
      - Summary
    ```

    Returns the parsed YAML as a dictionary. If the file doesn't exist
    or fails to parse, returns an empty list or dict as appropriate.

    Args:
        directory (str): Directory to look for `metadata.yaml`.

    Returns:
        dict or list: The YAML data, typically a dict with 'anki_tags' and 'ignore_sections'.
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
    Converts a PDF to one or more images, one image per page, using `pdf2image`.

    NOTE: The application currently expects only the first page to be used as an image.
          The return value is a list of PIL.Image objects (one for each PDF page).
    """
    return convert_from_path(path)


def _get_pdf_text(path: str) -> str:
    """
    Extracts text from a PDF file using `pdfminer`.

    (Currently, the main flow in this codebase does not rely on the raw text extraction
     of PDF files, but might be extended in the future.)
    """
    return extract_text(path)


def _get_img_uri(img: Image.Image) -> str:
    """
    Encodes a PIL Image as a base64 string, then prefixes it with a data URI scheme.

    Steps:
      1. Save the PIL image to an in-memory buffer as PNG.
      2. Read the buffer and base64-encode it.
      3. Format the string as 'data:image/png;base64,<encoded_data>'.

    Args:
        img (PIL.Image.Image): The image to be encoded.

    Returns:
        str: The base64-encoded data URI representing the image.
    """
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_png}"


def _get_plain_text(file_path: str) -> str:
    """
    Reads a file as plain UTF-8 text and returns the entire content as a string.

    Args:
        file_path (str): Path to the .txt file.

    Returns:
        str: Text content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _read_image_file(file_path: str) -> str:
    """
    Loads an image file (e.g., .png, .jpg) using PIL and converts it to a base64 data URI.

    Args:
        file_path (str): Path to the image file.

    Returns:
        str: Base64-encoded data URI of the image.
    """
    img = Image.open(file_path)
    return _get_img_uri(img)


def _read_pdf_file(file_path: str) -> str:
    """
    Converts the first page of a PDF into an image, then encodes that image as a base64 data URI.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Base64-encoded data URI of the first page’s image. Returns an empty string if no pages are found.
    """
    images = _get_image(file_path)
    if images:
        return _get_img_uri(images[0])
    return ""


# Dispatch table to map content types to their respective read functions.
READ_DISPATCH = {
    'text': _get_plain_text,
    'image': _read_image_file,
    'pdf': _read_pdf_file
}
