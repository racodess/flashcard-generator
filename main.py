"""
Purpose:
- Main entry-point and orchestration of the application.

1. Takes a directory path from the command line,
2. Recursively scans that directory,
3. For each discovered file:
    - Moves it into a used-files folder (to avoid reprocessing),
    - Copies it to the Anki media folder (collection.media) if appropriate,
    - Generates flashcards for it (or for the URLs found in .txt files).

- Execution: If you run python main.py <directory_path>, the script calls process_directory(...), which starts the scanning and processing of that directory.
"""
import os
import re
import sys
import shutil

from rich.console import Console

from utils import file_utils
from utils.flashcard_logger import logger
from utils.openai_generator import generate_flashcards

console = Console()


def get_anki_media_path():
    """
    - Returns the default `collection.media` path for Anki, depending on your operating system.
    """
    if sys.platform.startswith('win'):
        return os.path.expandvars(r'%APPDATA%\Anki2\User 1\collection.media')
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser('~/Library/Application Support/Anki2/User 1/collection.media')
    else:
        return os.path.expanduser('~/.local/share/Anki2/User 1/collection.media')


def move_file(file_path, used_dir, context):
    """
    - Moves a file from its original location into a mirrored structure under `used_dir`.
    - Uses `os.makedirs(..., exist_ok=True)` to create directories if needed, and `shutil.move(...)` to do the file move.
    """
    file_name = os.path.basename(file_path)
    target_dir = os.path.join(used_dir, context['relative_path'])
    os.makedirs(target_dir, exist_ok=True)

    new_file_path = os.path.join(target_dir, file_name)
    try:
        shutil.move(file_path, new_file_path)
        logger.debug("Moved %s to %s", file_path, new_file_path)
    except Exception as e:
        logger.error("Unable to move file %s: %s", file_path, e)

    return new_file_path


def copy_to_anki_media(file_path, content_type, anki_media_path):
    """
    - Copies the file over to the Anki media directory; should always exist if Anki is installed.
    - It places certain content (like PDFs) into a `_pdf_files` subdirectory within the Anki media directory for organization; required for linking the source file to the flashcards.
    - Places images in the Anki media directory; required for placing the image in the flashcard.
    """
    file_name = os.path.basename(file_path)
    try:
        if content_type in ['image']:
            shutil.copy2(file_path, anki_media_path)
        elif content_type == 'pdf':
            pdf_dir = os.path.join(anki_media_path, '_pdf_files')
            os.makedirs(pdf_dir, exist_ok=True)
            shutil.copy2(file_path, pdf_dir)
        else:
            # Copy everything else by default
            shutil.copy2(file_path, anki_media_path)

        logger.debug("Copied %s to Anki media path", file_name)
    except Exception as e:
        logger.error("Failed to copy %s to Anki media path: %s", file_name, e)


def process_file(file_path, context):
    """
    - This is central to how individual files are handled:

     1. Move the file to `used-files` as back-up,
     2. Copy it into Anki’s media folder,
     3. Determine the file’s “content type” (image, PDF, text, etc.) via `file_utils.get_content_type(...)`,
     4. Figure out the flashcard “type” (e.g., if the file is in a `problem_solving` subfolder, set `flashcard_type='problem'`),
     5. Finally, call `generate_flashcards(...)` from `openai_generator.py`.
    """
    # 1. Move file to used-files
    new_file_path = move_file(file_path, context['used_dir'], context)

    # 2. Identify content type (so we know how to copy it to Anki media)
    content_type = file_utils.get_content_type(new_file_path, url=None)
    if content_type == 'unsupported':
        logger.warning("Unsupported file type: %s. Skipping.", new_file_path)
        return False

    copy_to_anki_media(new_file_path, content_type, context['anki_media_path'])

    # 3. If 'problem_solving' is in the path, let's treat it as problem-solving flashcards
    flashcard_type = 'problem' if 'problem_solving' in os.path.normpath(context['relative_path']).split(os.sep) else 'general'

    # 4. Generate flashcards (single entry point)
    generate_flashcards(
        file_path=new_file_path,
        url=None,
        tags=context['tags'],
        flashcard_type=flashcard_type,
        anki_media_path=context['anki_media_path'],
    )
    return True


def process_url_in_txt(file_path, context):
    """
    - Sometimes `.txt` files contain URLs. This function:

     1. Moves the `.txt` file to `used-files` as back-up,
     2. Reads each line, searching for lines that match a URL pattern using regular expressions (`re.compile(...)`),
     3. For each URL, calls `generate_flashcards(...)`, telling the system to fetch that URL’s content.

    - If no URLs are found, it just processes the file normally (as with `process_file`).

    Returns:
        bool indicating if flashcards were generated.
    """
    file_name = os.path.basename(file_path)
    new_file_path = move_file(file_path, context['used_dir'], context)

    # Read lines to find URLs
    url_pattern = re.compile(r'(https?://[^\s]+)')
    with open(new_file_path, 'r', encoding='utf-8') as tf:
        lines = [line.strip() for line in tf if line.strip()]
    urls = [line for line in lines if url_pattern.match(line)]

    if not urls:
        logger.info("No URLs found in %s, proceeding as normal .txt", new_file_path)
        return process_file(new_file_path, context)

    any_generated = False
    logger.info("URLs found in %s. Generating flashcards from web page content.", new_file_path)

    for url in urls:
        # For simplicity, treat all these as 'general' flashcards
        generate_flashcards(
            file_path=None,
            url=url,
            tags=context['tags'],
            flashcard_type='general',
            anki_media_path=context['anki_media_path'],
        )
        any_generated = True

    return any_generated


def process_directory(directory_path, anki_media_path):
    """
    - Creates the `used-files` subfolder if it does not exist,
    - Invokes an internal, recursive helper `_process_directory_recursive(...)`,
    - Logs a warning if no files were successfully processed.
    """
    used_dir = os.path.join(directory_path, "used-files")
    os.makedirs(used_dir, exist_ok=True)

    processed_any = _process_directory_recursive(
        directory_path=directory_path,
        current_directory=directory_path,
        anki_media_path=anki_media_path,
        used_dir=used_dir
    )

    if not processed_any:
        logger.error("No files found or processed in the provided directory.")
    return processed_any


def _process_directory_recursive(directory_path, current_directory, anki_media_path, used_dir):
    """
    - Recursively descends into subdirectories. Uses:
        - `os.listdir(...)` to list directory entries,
        - Splits them into “files” and “subdirs”,
        - Reads local Anki tags from a `metadata.yaml` if present,
        - Processes each file with `process_file` or `process_url_in_txt`,
        - Calls itself on each subdirectory (ignores `used-files` directory).
    """
    if os.path.basename(current_directory) == "used-files":
        return False  # Skip the used-files folder

    try:
        entries = os.listdir(current_directory)
    except PermissionError:
        logger.warning("Permission denied for directory: %s. Skipping.", current_directory)
        return False

    entries_full_paths = [os.path.join(current_directory, entry) for entry in entries]
    files = [f for f in entries_full_paths if os.path.isfile(f) and os.path.basename(f) != "metadata.yaml"]
    subdirs = [d for d in entries_full_paths if os.path.isdir(d)]

    processed_something = False

    for fpath in files:
        local_tags = file_utils.read_metadata_tags(current_directory) if current_directory != directory_path else []
        # Log local tags for debugging
        console.log("[bold red] Local tags:", local_tags)

        relative_path = os.path.relpath(current_directory, directory_path)
        if relative_path == ".":
            relative_path = ""

        context = {
            'relative_path': relative_path,
            'used_dir': used_dir,
            'anki_media_path': anki_media_path,
            'tags': local_tags,
        }

        ext = os.path.splitext(fpath)[1].lower()
        if ext == '.txt':
            if process_url_in_txt(fpath, context):
                processed_something = True
        else:
            if process_file(fpath, context):
                processed_something = True

    for sd in subdirs:
        if os.path.basename(sd) == "used-files":
            continue # skips making flashcards out of anything in used-files directory
        if _process_directory_recursive(directory_path, sd, anki_media_path, used_dir):
            processed_something = True

    return processed_something


if __name__ == "__main__":
    """
    When you run the script from the terminal with a directory path:
    
    - The script checks the path is valid, calls `process_directory(...)`, and the entire pipeline flows from there.
    """
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <directory_path>")
        sys.exit(1)

    DIRECTORY_PATH = sys.argv[1]
    anki_media_path = get_anki_media_path()

    if not os.path.isdir(DIRECTORY_PATH):
        logger.error("The provided path is not a directory: %s", DIRECTORY_PATH)
        sys.exit(1)

    result = process_directory(DIRECTORY_PATH, anki_media_path)
    sys.exit(0 if result else 1)