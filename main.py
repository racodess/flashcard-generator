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
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from rich.console import Console
from utils import file_utils, flashcard_logger

console = Console()


def parse_arguments():
    """
    Parse command-line arguments to allow flexible, maintainable CLI usage.

    Example usage:
      python main.py --run-mode host
      python main.py --run-mode docker
      python main.py      (falls back to auto-detection logic)
    """
    parser = argparse.ArgumentParser(
        description="Flashcard generation CLI that can run either on the host or inside Docker."
    )
    parser.add_argument(
        "--run-mode",
        choices=["host", "docker"],
        default=None,
        help="Decide whether to run on 'host' or in 'docker'. "
             "If omitted, auto-detect if we are inside Docker or if Docker is available."
    )
    return parser.parse_args()


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


def _run_on_host():
    """
    Runs the application locally (on the host machine) using default file paths.

    Useful for development and testing.
    """
    flashcard_logger.logger.info(
        "Running on host..."
    )
    _process_directory(
        directory_path=file_utils.get_default_content_path(),
        anki_media_path=file_utils.get_anki_media_path(),
        pdf_viewer_path=file_utils.get_pdf_viewer_path()
    )
    sys.exit(0)


def _run_in_docker():
    """
    Runs the application locally (on the host machine) using default file paths.

    Useful for development and testing.
    """
    flashcard_logger.logger.info(
        "Running in docker container..."
    )
    _process_directory(
        directory_path=os.getenv(r'INPUT_DIRECTORY'),
        anki_media_path=os.getenv(r'ANKI_COLLECTION_MEDIA_PATH'),
        pdf_viewer_path=os.getenv(r'PDF_VIEWER_MEDIA_PATH')
    )
    sys.exit(0)


def _initialize_container():
    """
    Spawns a Docker container to run the application inside Docker, passing necessary
    environment variables and mounting host paths.
    """
    flashcard_logger.logger.info(
        "Attempting to initializing a Docker container..."
    )
    if not file_utils.is_docker_available():
        flashcard_logger.logger.error(
            "Docker is not installed or not running."
        )
        sys.exit(1)

    flashcard_logger.logger.info(
        "Checking Docker image..."
    )
    file_utils.build_docker_image()

    # We reload .env to ensure we have all environment variables
    load_dotenv(
        dotenv_path=".env",
        override=True
    )
    # The Docker command
    docker_cmd = [
        "docker", "run", "--rm", "-it",
        # So the code knows it's inside Docker
        "-e", "IN_DOCKER=1",
        # Pass environment variables to container
        "-e", f"OPENAI_API_KEY={os.getenv(r'OPENAI_API_KEY')}",
        "-e", f"ANKI_CONNECT_URL={os.getenv(r'ANKI_CONNECT_URL') or 'http://localhost:8765'}",
        "-e", r"INPUT_DIRECTORY=/app/content",
        "-e", r"ANKI_COLLECTION_MEDIA_PATH=/app/Anki-collection-media",
        "-e", r"PDF_VIEWER_MEDIA_PATH=/app/Ankifiles",
        # Mount the host's input directory to /app/content in container
        "-v", f"{os.getenv(r'INPUT_DIRECTORY')}:/app/content",
        # Mount the host's Anki collection.media directory
        "-v", f"{os.getenv(r'ANKI_COLLECTION_MEDIA_PATH')}:/app/Anki-collection-media",
        # Mount the host's Anki add-on 'pdf viewer' directory
        "-v", f"{os.getenv(r'PDF_VIEWER_MEDIA_PATH')}:/app/Ankifiles",
        "flashcard-app",
        # Command inside the container:
        "python", "main.py"
    ]
    console.print(
        "[green]Restarting application within a docker container...[/green]"
    )
    result_code = subprocess.call(docker_cmd)
    sys.exit(result_code)


def main():
    """
    Main CLI entry point. Decides if we run on host or in Docker.

    The order of logic is:
      1. Parse CLI for --run-mode.
      2. If run-mode is 'host' -> run_on_host().
      3. If run-mode is 'docker' -> run_in_docker().
      4. If no run-mode is specified:
            - Check if we are already inside Docker: if yes, run_on_host().
            - Else, check if Docker is installed: if yes, default to docker, else run_on_host().
    """
    args = parse_arguments()

    # If user explicitly sets run-mode to 'host' or 'docker', do so:
    if args.run_mode == "host":
        _run_on_host()
    elif args.run_mode == "docker":
        _initialize_container()
    else:
        if file_utils.is_inside_docker():
            # We are *already* in Docker. Just run on host logic now (no spawn).
            _run_in_docker()
        else:
            if not file_utils.is_docker_available():
                flashcard_logger.logger.warning("Docker is not installed or not running. Running on host.")
                _run_on_host()
            else:
                # By default, if Docker is available and user didn't specify, run Docker
                _initialize_container()


if __name__ == "__main__":
    main()