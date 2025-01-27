"""
Main entry-point and orchestration of the application.

1. Takes a directory path from the command line,
2. Recursively scans that directory,
3. For each discovered file:
    - Moves it into a used-files folder (to avoid reprocessing),
    - Copies it to the Anki media folder (collection.media) if appropriate,
    - Generates flashcards for it (or for the URLs found in .txt files).

- Execution: If you run python host.py <directory_path>, the script calls process_directory(...), which starts the scanning and processing of that directory.
"""
import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from rich.console import Console
from utils import file_utils, flashcard_logger
from utils.flashcard_logger import logger

console = Console()


def _process_directory(
        directory_path,
        anki_media_path,
        pdf_viewer_path
):
    """
    Orchestrates the processing of the given directory.

    1. Creates 'used-files' folder if it doesn't exist,
    2. Calls `_process_directory_recursive(...)` to traverse the directory,
    3. Logs an error if no files were successfully processed.

    Args:
        directory_path (str): The path that the user provided via command line.
        anki_media_path (str): The resolved path to Anki's 'collection.media' folder.
        pdf_viewer_path (str): The path to the Anki add-on 'pdf viewer and editor' required directory.

    Returns:
        bool: True if any file was successfully processed; False otherwise.
    """
    used_dir = os.path.join(directory_path, "used-files")
    # Create the 'used-files' subfolder if it does not already exist
    os.makedirs(used_dir, exist_ok=True)

    # Start the recursive processing from this directory
    processed_any = _process_directory_recursive(
        directory_path=directory_path,
        current_directory=directory_path,
        anki_media_path=anki_media_path,
        pdf_viewer_path=pdf_viewer_path,
        used_dir=used_dir
    )

    # If no files were found or processed, log an error
    if not processed_any:
        flashcard_logger.logger.error("No files found or processed in the provided directory.")
    return processed_any


def _process_directory_recursive(
        directory_path,
        current_directory,
        anki_media_path,
        pdf_viewer_path,
        used_dir
):
    """
    Recursively descends into each subdirectory of 'directory_path' and processes files.

    It performs the following logic:
      - Skip if the current directory is named 'used-files', to avoid reprocessing moved files.
      - Attempt to list all entries in the directory.
      - Collect the files (excluding 'metadata.yaml') and subdirectories.
      - For each file:
          * Build 'metadata' by reading any local 'metadata.yaml' (via file_utils),
          * Build a 'context' dict that includes the relative path, used_dir, etc.
          * If the file is a .txt, call `_process_url(...)`,
            otherwise call `_process_file(...)`.
      - For each subdirectory (except 'used-files'), recursively call `_process_directory_recursive`.

    Args:
        directory_path (str): The root directory we started with.
        current_directory (str): The directory we are currently scanning.
        anki_media_path (str): Path to Anki's 'collection.media' folder.
        pdf_viewer_path (str): The path to the Anki add-on 'pdf viewer and editor' required directory.
        used_dir (str): Path to the 'used-files' folder.

    Returns:
        bool: True if any file was processed in this directory or subdirectories, False otherwise.
    """
    # Avoid reprocessing items in the 'used-files' directory
    if os.path.basename(current_directory) == "used-files":
        return False

    try:
        entries = os.listdir(current_directory)
    except PermissionError:
        # If we do not have permission to read a directory, log and skip
        flashcard_logger.logger.warning("Permission denied for directory: %s. Skipping.", current_directory)
        return False

    # Construct full paths for each entry in the current directory
    entries_full_paths = [os.path.join(current_directory, entry) for entry in entries]

    # Separate files and subdirectories (ignoring 'metadata.yaml' in file list)
    files = [f for f in entries_full_paths if os.path.isfile(f) and os.path.basename(f) != "metadata.yaml"]
    subdirs = [d for d in entries_full_paths if os.path.isdir(d)]

    processed_something = False

    # Process each file in the current directory
    for fpath in files:
        # Gather tags and sections to ignore by reading from metadata.yaml if it exists
        metadata = {
            "anki_tags": file_utils.get_tags(current_directory) if current_directory != directory_path else [],
            "ignore_sections": file_utils.get_ignore_list(current_directory) if current_directory != directory_path else [],
        }

        # Determine the path of the current directory relative to the root directory
        relative_path = os.path.relpath(current_directory, directory_path)
        if relative_path == ".":
            relative_path = ""

        # Build the context dict to pass around
        context = {
            'relative_path': relative_path,
            'used_dir': used_dir,
            'anki_media_path': anki_media_path,
            'pdf_viewer_path': pdf_viewer_path,
            'metadata': metadata,
        }

        # Check if the file is a .txt; if so, look for URLs. Otherwise, process as normal.
        ext = os.path.splitext(fpath)[1].lower()
        if ext == '.txt':
            if file_utils.process_url(fpath, context):
                processed_something = True
        else:
            if file_utils.process_file(fpath, context):
                processed_something = True

    # Recursively process each subdirectory
    for sd in subdirs:
        # Skip the 'used-files' subdirectory to avoid reprocessing moved files
        if os.path.basename(sd) == "used-files":
            continue
        if _process_directory_recursive(
                directory_path=directory_path,
                current_directory=sd,
                anki_media_path=anki_media_path,
                pdf_viewer_path=pdf_viewer_path,
                used_dir=used_dir
        ):
            processed_something = True

    return processed_something


def main():
    """Decide whether to run local or in Docker based on environment variables."""
    load_dotenv()

    if file_utils.is_inside_docker():
        logger.info("Running in Docker container...")
        _process_directory(
            directory_path=os.getenv("INPUT_DIRECTORY"),
            anki_media_path=os.getenv("ANKI_COLLECTION_MEDIA_PATH"),
            pdf_viewer_path=os.getenv("PDF_VIEWER_MEDIA_PATH")
        )
    else:
        logger.info("Running in host...")
        _process_directory(
            directory_path=file_utils.get_default_content_path(),
            anki_media_path=file_utils.get_anki_media_path(),
            pdf_viewer_path=file_utils.get_pdf_viewer_path()
        )
    sys.exit(0)

if __name__ == "__main__":
    main()
