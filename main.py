import os
import sys
import shutil
import subprocess

from rich.console import Console
from rich import print as rprint

console = Console()

processed_any_files = False  # Global flag to track if any files were processed.

def determine_collection_media_path():
    if sys.platform.startswith('win'):
        return os.path.expandvars(r'%APPDATA%\Anki2\User 1\collection.media')
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser('~/Library/Application Support/Anki2/User 1/collection.media')
    else:
        return os.path.expanduser('~/Documents/Anki2/User 1/collection.media')


def process_file(file_path, used_dir, tags):
    global processed_any_files

    base_dir = os.path.dirname(file_path)
    rel_path = os.path.relpath(base_dir, DIRECTORY_PATH)
    if rel_path == '.':
        rel_path = ''

    target_dir = os.path.join(used_dir, rel_path)
    os.makedirs(target_dir, exist_ok=True)

    new_file_path = os.path.join(target_dir, os.path.basename(file_path))
    shutil.move(file_path, new_file_path)

    collection_media_path = determine_collection_media_path()
    os.makedirs(collection_media_path, exist_ok=True)

    file_ext = os.path.splitext(new_file_path)[1].lower()
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        shutil.copy2(new_file_path, collection_media_path)
    elif file_ext == '.pdf':
        pdf_dir = os.path.join(collection_media_path, '_pdf_files')
        os.makedirs(pdf_dir, exist_ok=True)
        shutil.copy2(new_file_path, pdf_dir)
    else:
        shutil.copy2(new_file_path, collection_media_path)

    is_problem_solving = 'problem_solving' in os.path.normpath(rel_path).split(os.sep)

    command = [sys.executable, 'generator.py', new_file_path, os.path.basename(new_file_path), collection_media_path] + tags

    if is_problem_solving:
        command.append('--code')

    subprocess.run(command)

    processed_any_files = True


tags = []
def process_directory_recursive(current_directory, used_dir):
    if os.path.basename(current_directory) == "used-files":
        return

    try:
        entries = os.listdir(current_directory)
    except PermissionError:
        rprint(f"[yellow]Warning: Permission denied for directory {current_directory}. Skipping.[/yellow]")
        return

    entries_full_paths = [os.path.join(current_directory, e) for e in entries]

    files = [f for f in entries_full_paths if os.path.isfile(f)]
    subdirs = [d for d in entries_full_paths if os.path.isdir(d)]

    tags_file = os.path.join(current_directory, "tags.txt")
    tags_exist = False
    if os.path.isfile(tags_file):
        tags_exist = True
        # Read tags
        with open(tags_file, 'r', encoding='utf-8') as tf:
            tags = [line.strip() for line in tf if line.strip()]

    files_to_process = [f for f in files if os.path.basename(f) != "tags.txt"]

    if files_to_process:
        if not tags_exist:
            rprint(f"[yellow]Warning: No tags.txt found in {current_directory}. Proceeding without flashcard tags. Your flashcards will be imported to Anki without tags.[/yellow]")
        for f in files_to_process:
            process_file(f, used_dir, tags)

    for sd in subdirs:
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

    used_dir = os.path.join(DIRECTORY_PATH, "used-files")
    if not os.path.exists(used_dir):
        os.makedirs(used_dir)

    process_directory_recursive(DIRECTORY_PATH, used_dir)

    if not processed_any_files:
        rprint("[red]Error: No files found to process.[/red]")