import os
import sys
import subprocess

def process_directory(directory_path):
    # Get a list of files in the directory
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path)]
    # Sort files for consistent processing order
    files.sort()

    for file_path in files:
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue
        # Call the main script for each file
        subprocess.run([sys.executable, 'generator.py', file_path])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory_path>")
        sys.exit(1)

    DIRECTORY_PATH = sys.argv[1]

    if not os.path.isdir(DIRECTORY_PATH):
        print(f"The provided path is not a directory: {DIRECTORY_PATH}")
        sys.exit(1)

    process_directory(DIRECTORY_PATH)