import os
import sys
import subprocess
import shutil

def process_directory(directory_path):
    # Ensure "used-files" directory exists
    used_dir = os.path.join(directory_path, "used-files")
    if not os.path.exists(used_dir):
        os.makedirs(used_dir)

    # Get a list of files in the directory
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path)]
    # Sort files for consistent processing order
    files.sort()

    for file_path in files:
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue

        # Move the file to the used-files directory
        new_file_path = os.path.join(used_dir, os.path.basename(file_path))
        shutil.move(file_path, new_file_path)

        # Determine the anki collection.media folder path depending on the OS
        if sys.platform.startswith('win'):
            collection_media_path = os.path.expandvars(r'%APPDATA%\Anki2\User 1\collection.media')
        elif sys.platform.startswith('darwin'):
            collection_media_path = os.path.expanduser('~/Library/Application Support/Anki2/User 1/collection.media')
        else:
            collection_media_path = os.path.expanduser('~/Documents/Anki2/User 1/collection.media')

        os.makedirs(collection_media_path, exist_ok=True)

        # Check file extension
        file_ext = os.path.splitext(new_file_path)[1].lower()
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
            # Copy images directly into the collection.media folder
            shutil.copy2(new_file_path, collection_media_path)
        elif file_ext == '.pdf':
            # For PDF files, use or create a _pdf_files directory within collection.media
            pdf_dir = os.path.join(collection_media_path, '_pdf_files')
            os.makedirs(pdf_dir, exist_ok=True)
            shutil.copy2(new_file_path, pdf_dir)

        # Call the generator script with the new file path and its base name
        subprocess.run([sys.executable, 'generator.py', new_file_path, os.path.basename(new_file_path)])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory_path>")
        sys.exit(1)

    DIRECTORY_PATH = sys.argv[1]

    if not os.path.isdir(DIRECTORY_PATH):
        print(f"The provided path is not a directory: {DIRECTORY_PATH}")
        sys.exit(1)

    process_directory(DIRECTORY_PATH)
