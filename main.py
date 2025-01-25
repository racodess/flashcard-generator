"""
Main entry-point and orchestration of the application.

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
import subprocess

from dotenv import load_dotenv

from rich.console import Console

from utils import file_utils
from utils.flashcard_logger import logger
from utils.openai_generator import generate_flashcards

console = Console()


def _is_inside_docker():
    """
    Simple check to see if we are *inside* a Docker container.
    """
    return os.getenv("IN_DOCKER") == "1" or os.path.exists("/.dockerenv")


def _is_docker_available():
    """
    Check if Docker is installed on the user's system by calling 'docker --version'.
    Returns True if Docker CLI is available, otherwise False.
    """
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except Exception:
        return False


def _build_docker_image():
    r"""
    Check if 'flashcard-app' Docker image exists. If not, build it.
    """
    # This command returns an empty string if the image doesn't exist
    result = subprocess.run(["docker", "images", "-q", "flashcard-app"], capture_output=True, text=True)
    if not result.stdout.strip():
        console.print("[yellow]Docker image 'flashcard-app' not found. Building...[/yellow]")
        build_cmd = ["docker", "build", "-t", "flashcard-app", "."]
        build_result = subprocess.run(build_cmd)
        if build_result.returncode != 0:
            logger.error("Failed to build Docker image 'flashcard-app'. Make sure Docker Desktop is installed and running.")
            sys.exit(1)
        else:
            console.print("[green]Successfully built Docker image 'flashcard-app'.[/green]")


def _set_media_copy(
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
        if content_type in ['image']:
            shutil.copy2(file_path, anki_media_path)
        # If the file is a PDF:
        elif content_type in ['pdf']:
            # For backup and syncing of all pdf files used within Anki
            pdf_dir = os.path.join(anki_media_path, '_pdf_files')
            os.makedirs(pdf_dir, exist_ok=True)
            shutil.copy2(file_path, pdf_dir)

            # Ensures the pdf file is accessible within Anki flashcards
            # during review using the 'pdf viewer and editor' Anki add-on
            os.makedirs(pdf_viewer_path, exist_ok=True)
            shutil.copy2(file_path, pdf_viewer_path)
        else:
            return

        logger.debug("Copied %s to Anki media path(s)", file_name)
    except Exception as e:
        # Log any failures during the copy
        logger.error("Failed to copy %s to Anki media path: %s", file_name, e)


def _set_used_file(
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


def _process_file(file_path, context):
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
    new_file_path = _set_used_file(file_path, context['used_dir'], context)

    # 2. Determine content type to decide how to handle within Anki
    content_type = file_utils.get_content_type(new_file_path, url=None)
    if content_type == 'unsupported':
        logger.warning("Unsupported file type: %s. Skipping.", new_file_path)
        return False

    # 3. Copy file into the Anki media folder in the correct location
    _set_media_copy(new_file_path, content_type, context['anki_media_path'], context['pdf_viewer_path'])

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


def _process_url(file_path, context):
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
    new_file_path = _set_used_file(file_path, context['used_dir'], context)

    # 2. Use a regex to match URL patterns in each line
    url_pattern = re.compile(r'(https?://[^\s]+)')
    with open(new_file_path, 'r', encoding='utf-8') as tf:
        lines = [line.strip() for line in tf if line.strip()]
    urls = [line for line in lines if url_pattern.match(line)]

    # If no URLs are found, treat the file as a normal text file
    if not urls:
        logger.info("No URLs found in %s, proceeding as normal .txt", new_file_path)
        return _process_file(new_file_path, context)

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
        logger.error("No files found or processed in the provided directory.")
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
        logger.warning("Permission denied for directory: %s. Skipping.", current_directory)
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
            if _process_url(fpath, context):
                processed_something = True
        else:
            if _process_file(fpath, context):
                processed_something = True

    # Recursively process each subdirectory
    for sd in subdirs:
        # Skip the 'used-files' subdirectory to avoid reprocessing moved files
        if os.path.basename(sd) == "used-files":
            continue
        if _process_directory_recursive(directory_path, sd, anki_media_path, pdf_viewer_path, used_dir):
            processed_something = True

    return processed_something


def _main():
    if len(sys.argv) != 1:
        logger.error('Usage: python main.py')
        sys.exit(1)

    result = _process_directory(
        directory_path=os.getenv(r'INPUT_DIRECTORY'),
        anki_media_path=os.getenv(r'ANKI_COLLECTION_MEDIA_PATH'),
        pdf_viewer_path=os.getenv(r'PDF_VIEWER_MEDIA_PATH')
    )
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    if _is_inside_docker():
        console.print(
            "[green]Docker container detected. Running inside container...[/green]"
        )
        _main()
    else:
        if not _is_docker_available():
            logger.error("Usage: Docker must be installed.")
            sys.exit(1)

        console.print(
            "[green]Checking docker image...[/green]"
        )
        _build_docker_image()

        load_dotenv(
            dotenv_path=".env",
            override=True
        )
        docker_cmd = [
            # The command to run container
            "docker", "run", "--rm", "-it",
            # So the code knows it's inside Docker
            "-e", "IN_DOCKER=1",
            # Pass environment variables to container
            "-e", f"OPENAI_API_KEY={os.getenv(r'OPENAI_API_KEY')}",
            "-e", f"ANKI_CONNECT_URL={os.getenv(r'ANKI_CONNECT_URL') or 'http://host.docker.internal:8765'}",
            "-e", "INPUT_DIRECTORY=/app/content",
            "-e", "ANKI_COLLECTION_MEDIA_PATH=/app/Anki-collection-media",
            "-e", "PDF_VIEWER_MEDIA_PATH=/app/Ankifiles",
            # Mount the host's input directory to container:
            # Contains all source material being used for flashcard creation
            "-v", f"{os.getenv(r'INPUT_DIRECTORY')}:/app/content",
            # Mount the host's Anki collection.media directory to container:
            # Default Anki media path which allows backups and syncing of files
            "-v", f"{os.getenv(r'ANKI_COLLECTION_MEDIA_PATH')}:/app/Anki-collection-media",
            # Mount the host's Anki add-on 'pdf viewer and editor' media directory to container:
            # Required by the add-on to link PDFs to flashcards as references
            "-v", f"{os.getenv(r'PDF_VIEWER_MEDIA_PATH')}:/app/Ankifiles",
            "flashcard-app",
            # The command inside the container
            "python", "main.py"
        ]
        console.print(
            f"[green]Restarting in docker container...[/green]"
        )
        result_code = subprocess.call(
            docker_cmd
        )
        sys.exit(result_code)
