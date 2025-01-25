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
import re
import sys
import yaml
import base64
import shutil
import subprocess
from PIL import Image
from rich.console import Console
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
from utils.flashcard_logger import logger
from utils.openai_generator import generate_flashcards


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


def get_default_content_path():
    r"""
    Returns the path to the default 'source material' content folder.

    By default, this is the `content` folder within the working directory of this application.
    Flashcards will be generated based on the files within this content folder.

    Adjust as necessary if your desired configuration from this default.
    """
    if sys.platform.startswith('win'):
        return os.path.expandvars(
            r'.\content'
        )
    else:
        return os.path.expandvars(
            r'./content'
        )


def get_anki_media_path():
    r"""
    Returns the path to the default Anki 'collection.media' folder.

    collection_media always refers to Anki's default media path that stores backups,
    and allows syncing of media files.

    Windows: '%APPDATA%\Anki2\'.
    MacOS: '~/Library/Application Support/Anki2'.
    Linux/UNIX: '~/.local/share/Anki2'.

    Adjust as necessary if your configuration differs from these defaults.
    """
    # Determine the operating system and set the default paths accordingly
    if sys.platform.startswith('win'):
        return os.path.expandvars(
            r'%APPDATA%\Anki2\User 1\collection.media'
        )
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser(
            r'~/Library/Application Support/Anki2/User 1/collection.media'
        )
    else:
        return os.path.expanduser(
            r'~/.local/share/Anki2/User 1/collection.media'
        )


def get_pdf_viewer_path():
    r"""
    Returns the path to the folder required by the Anki add-on 'pdf viewer and editor',
    for access and linking of PDF files within Anki flashcards.

    pdf_viewer_path always refers to the path required by the 'pdf viewer and editor' Anki add-on,
    and allows it to access the files as reference material during reviews on any OS. This is required
    due to macOS sandboxing, which prevents the add-on from accessing files directly from Anki's default
    media path.

    MacOS: '~/Ankifiles'.
    Windows/Linux/UNIX: '~/Documents/Ankifiles'.

    Adjust as necessary if your configuration differs from these defaults.
    """
    # Determine the operating system and set the default paths accordingly
    if sys.platform.startswith('win'):
        return os.path.expanduser(
            r'~\Documents\Ankifiles'
        )
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser(
            r'~/Ankifiles'
        )
    else:
        return os.path.expanduser(
            r'~/Documents/Ankifiles'
        )


def get_data(
        file_path: str,
        content_type: str
):
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
    print()
    console.rule("[bold red]Anki Tags[/bold red]")
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


def get_content_type(
        file_path: str,
        url: str = None
) -> str:
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


def set_media_copy(
        file_path,
        content_type,
        anki_media_path,
        pdf_viewer_path
):
    """
    Copies the file to the specified Anki media directory.

    The behavior varies by file `content_type`:
      - Images are copied directly into the top-level of the Anki media folder.
      - PDFs are copied into a subfolder called '_pdf_files' within the Anki media folder.
      - Other file types (if supported) are copied to the top-level folder by default.

    Args:
        file_path (str): Full path to the source file.
        content_type (str): Type of the content (image, pdf, or other).
        anki_media_path (str): The resolved path to Anki's 'collection.media' directory.
        pdf_viewer_path (str): The path to the Anki add-on 'pdf viewer and editor' required directory.

    It logs an error if the copy fails for any reason (e.g., permission errors).
    """
    file_name = os.path.basename(file_path)
    try:
        # If the file is an image, copy it directly to the default Anki media folder
        # Images can be accessed, backed-up, and synced directly from the Anki media folder
        if content_type in ['image']:
            shutil.copy2(
                file_path,
                anki_media_path
            )
        # If the file is a PDF, backup/syncing is done from Anki's media folder,
        # but accessing within flashcards is done from Anki add-on 'pdf viewer and editor' required folder.
        elif content_type in ['pdf']:
            # Only used for backup and syncing of pdf files used within Anki
            pdf_anki_backup_dir = os.path.join(
                anki_media_path,
                '_pdf_files'
            )
            os.makedirs(
                pdf_anki_backup_dir,
                exist_ok=True
            )
            shutil.copy2(
                file_path,
                pdf_anki_backup_dir
            )
            # Ensures the pdf file is accessible within Anki flashcards
            pdf_viewer_access_dir = pdf_viewer_path
            os.makedirs(
                pdf_viewer_access_dir,
                exist_ok=True
            )
            shutil.copy2(
                file_path,
                pdf_viewer_access_dir
            )
        else:
            return

        logger.debug("Copied %s to Anki media path(s)", file_name)
    except Exception as e:
        # Log any failures during the copy
        logger.error("Failed to copy %s to Anki media path: %s", file_name, e)


def set_used_file(
        file_path,
        used_dir,
        context
):
    """
    Moves a file from its current location into a mirrored subdirectory under `used_dir`.

    The 'used-files' directory is meant to store files that have been processed,
    preventing them from being re-processed in subsequent runs. The subdirectory
    structure under `used_dir` mirrors the original folder hierarchy.

    Args:
        file_path (str): The full path of the file being moved.
        used_dir (str): The full path to the 'used-files' folder.
        context (dict): Holds contextual info like the relative path from
                        the scanned directory, among others.

    Returns:
        str: The new file path after being moved.
    """
    file_name = os.path.basename(file_path)
    # Construct the subdirectory in 'used_dir' that mirrors original location
    target_dir = os.path.join(used_dir, context['relative_path'])
    os.makedirs(target_dir, exist_ok=True)

    # Append the file name to the target directory path
    new_file_path = os.path.join(target_dir, file_name)
    try:
        shutil.move(file_path, new_file_path)
        logger.debug("Moved %s to %s", file_path, new_file_path)
    except Exception as e:
        # Log issues if the file move fails (e.g., permission, existing file with the same name)
        logger.error("Unable to move file %s: %s", file_path, e)

    return new_file_path


def is_inside_docker():
    """
    Simple check to see if we are *inside* a Docker container.
    """
    return os.getenv("IN_DOCKER") == "1" or os.path.exists("/.dockerenv")


def is_docker_available():
    """
    Check if Docker is installed on the user's system by calling 'docker --version'.
    Returns True if Docker CLI is available, otherwise False.
    """
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            capture_output=True
        )
        return True
    except Exception:
        return False


def build_docker_image():
    r"""
    Check if 'flashcard-app' Docker image exists. If not, build it.
    """
    # This command returns an empty string if the image doesn't exist
    result = subprocess.run(
        ["docker", "images", "-q", "flashcard-app"],
        capture_output=True,
        text=True
    )
    if not result.stdout.strip():
        logger.info(
            "Docker image 'flashcard-app' not found. Building..."
        )
        build_cmd = [
            "docker", "build", "-t", "flashcard-app", "."
        ]
        build_result = subprocess.run(
            build_cmd
        )
        if build_result.returncode != 0:
            logger.error("Failed to build Docker image 'flashcard-app'. Make sure Docker Desktop is installed and running.")
            sys.exit(1)
        else:
            console.print("[green]Successfully built Docker image 'flashcard-app'.[/green]")


def process_file(file_path, context):
    """
    Primary handler for processing individual non-.txt files (images, PDFs, etc.).

    Steps:
      1. Move the file to `used-files` as a back-up,
      2. Determine the file’s content type (image, PDF, text, etc.) via file_utils,
      3. Copy the file into Anki’s media folder according to the content type,
      4. Infer the flashcard "type" (e.g., 'problem' for files under 'problem_solving' subfolder),
      5. Call `generate_flashcards(...)` to create relevant flashcards for the file.

    Returns:
        bool: True if flashcard generation was successful, False if skipped/unsupported.
    """
    # 1. Move file to the 'used-files' folder
    new_file_path = set_used_file(file_path, context['used_dir'], context)

    # 2. Determine content type to decide how to handle within Anki
    content_type = get_content_type(new_file_path, url=None)
    if content_type == 'unsupported':
        logger.warning("Unsupported file type: %s. Skipping.", new_file_path)
        return False

    # 3. Copy file into the Anki media folder in the correct location
    set_media_copy(new_file_path, content_type, context['anki_media_path'], context['pdf_viewer_path'])

    # 4. Infer flashcard type based on directory naming convention
    #    If 'problem_solving' is in path, we treat it as problem-solving
    flashcard_type = 'problem' if 'problem_solving' in os.path.normpath(context['relative_path']).split(os.sep) else 'general'

    # 5. Generate flashcards for this file
    generate_flashcards(
        file_path=new_file_path,
        url=None,
        metadata=context['metadata'],
        flashcard_type=flashcard_type,
        anki_media_path=context['anki_media_path'],
        pdf_viewer_path=context['pdf_viewer_path']
    )
    return True


def process_url(file_path, context):
    """
    Processes a .txt file that may contain URLs.

    Steps:
      1. Move the .txt file to `used-files` (back-up),
      2. Read the file line by line and check each line for a URL pattern,
      3. For each URL found, call `generate_flashcards(...)`,
      4. If no URLs are found, fallback to `_process_file(...)` to handle the file normally.

    Args:
        file_path (str): Path to the .txt file.
        context (dict): Similar context dictionary as used in _process_file.

    Returns:
        bool: True if any flashcards were generated, False otherwise.
    """
    # 1. Move the .txt file to 'used-files'
    new_file_path = set_used_file(file_path, context['used_dir'], context)

    # 2. Use a regex to match URL patterns in each line
    url_pattern = re.compile(r'(https?://[^\s]+)')
    with open(new_file_path, 'r', encoding='utf-8') as tf:
        lines = [line.strip() for line in tf if line.strip()]
    urls = [line for line in lines if url_pattern.match(line)]

    # If no URLs are found, treat the file as a normal text file
    if not urls:
        logger.info("No URLs found in %s, proceeding as normal .txt", new_file_path)
        return process_file(new_file_path, context)

    # Otherwise, generate flashcards from each URL discovered
    any_generated = False
    logger.info("URLs found in %s. Generating flashcards from web page content.", new_file_path)

    for url in urls:
        # For URL-based flashcards, we use 'url' as the flashcard_type
        generate_flashcards(
            file_path=None,
            url=url,
            metadata=context['metadata'],
            flashcard_type='url',
            anki_media_path=context['anki_media_path'],
            pdf_viewer_path=context['pdf_viewer_path']
        )
        any_generated = True

    return any_generated


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
