import os
import sys
import subprocess
import shutil
from rich import print as rprint

processed_any_files = False  # Global flag to track if any files were processed.

def determine_collection_media_path():
    if sys.platform.startswith('win'):
        return os.path.expandvars(r'%APPDATA%\Anki2\User 1\collection.media')
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser('~/Library/Application Support/Anki2/User 1/collection.media')
    else:
        return os.path.expanduser('~/Documents/Anki2/User 1/collection.media')

def process_file(file_path, used_dir, tags):
    """
    Process an individual file:
    - Move it into the corresponding folder in used-files.
    - Copy it into Anki's collection.media (or a subfolder like _pdf_files for PDFs).
    - Run generator.py on it with the provided tags.
    """

    global processed_any_files

    # If this directory structure doesn't exist in used_dir, create it.
    # For example, if file_path is flashcard-data/subfolderA/file.png
    # and used_dir is flashcard-data/used-files
    # we want flashcard-data/used-files/subfolderA/file.png
    base_dir = os.path.dirname(file_path)
    # Find relative path of current file directory to the top-level directory
    # Assuming DIRECTORY_PATH is top-level, we can reconstruct:
    rel_path = os.path.relpath(base_dir, DIRECTORY_PATH)
    if rel_path == '.':
        rel_path = ''  # top-level files go directly in used-files

    target_dir = os.path.join(used_dir, rel_path)
    os.makedirs(target_dir, exist_ok=True)

    new_file_path = os.path.join(target_dir, os.path.basename(file_path))
    shutil.move(file_path, new_file_path)

    # Ensure collection.media directory exists
    collection_media_path = determine_collection_media_path()
    os.makedirs(collection_media_path, exist_ok=True)

    # Check file extension and copy appropriately
    file_ext = os.path.splitext(new_file_path)[1].lower()
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        shutil.copy2(new_file_path, collection_media_path)
    elif file_ext == '.pdf':
        pdf_dir = os.path.join(collection_media_path, '_pdf_files')
        os.makedirs(pdf_dir, exist_ok=True)
        shutil.copy2(new_file_path, pdf_dir)
    else:
        # For other file types, if needed, we can handle differently or just copy directly
        shutil.copy2(new_file_path, collection_media_path)

    # Call generator.py with the file and tags
    # The instructions: pass tags if and only if other files aside from tags.txt exist.
    # We are at this point only processing a file that is not tags.txt, so tags exist.
    subprocess.run([sys.executable, 'generator.py', new_file_path, os.path.basename(new_file_path)] + tags)

    processed_any_files = True

def process_directory_recursive(current_directory, used_dir):
    """
    Recursively process a directory:
    - Skip the used-files directory and its contents.
    - In each directory (except used-files):
        * Check for tags.txt
        * If tags.txt found, read tags
        * Process all other files (not tags.txt)
        * If no other files, do not call generator.py
        * Recurse into subdirectories (except used-files)
    """

    # If this is the used-files directory, skip processing entirely
    if os.path.basename(current_directory) == "used-files":
        return

    # Gather files and subdirectories
    try:
        entries = os.listdir(current_directory)
    except PermissionError:
        rprint(f"[yellow]Warning: Permission denied for directory {current_directory}. Skipping.[/yellow]")
        return

    entries_full_paths = [os.path.join(current_directory, e) for e in entries]

    # Separate files and directories
    files = [f for f in entries_full_paths if os.path.isfile(f)]
    subdirs = [d for d in entries_full_paths if os.path.isdir(d)]

    # Check for tags.txt
    tags_file = os.path.join(current_directory, "tags.txt")
    tags = []
    tags_exist = False
    if os.path.isfile(tags_file):
        tags_exist = True
        # Read tags
        with open(tags_file, 'r', encoding='utf-8') as tf:
            tags = [line.strip() for line in tf if line.strip()]

    # Filter out tags.txt from files to process
    files_to_process = [f for f in files if os.path.basename(f) != "tags.txt"]

    # If there are files to process, handle tags
    if files_to_process:
        if not tags_exist:
            # Only warn if there are files to process without tags
            rprint(f"[yellow]Warning: No tags.txt found in {current_directory}. Proceeding without flashcard tags. Your flashcards will be imported to Anki without tags.[/yellow]")
        # Process each file
        for f in files_to_process:
            process_file(f, used_dir, tags)

    # Recurse into subdirectories (except used-files)
    for sd in subdirs:
        # Ignore used-files subdir
        if os.path.basename(sd) == "used-files":
            continue
        process_directory_recursive(sd, used_dir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory_path>")
        sys.exit(1)

    DIRECTORY_PATH = sys.argv[1]

    if not os.path.isdir(DIRECTORY_PATH):
        print(f"The provided path is not a directory: {DIRECTORY_PATH}")
        sys.exit(1)

    # Ensure "used-files" directory exists at top-level
    used_dir = os.path.join(DIRECTORY_PATH, "used-files")
    if not os.path.exists(used_dir):
        os.makedirs(used_dir)

    # Recursively process the directory
    process_directory_recursive(DIRECTORY_PATH, used_dir)

    # If no files were processed at all, print an error in red text
    if not processed_any_files:
        rprint("[red]Error: No files found to process.[/red]")