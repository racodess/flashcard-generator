import os
import subprocess
import sys

from utils.flashcard_logger import logger


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
            logger.info("Successfully built Docker image 'flashcard-app'.")


def load_env_file(env_path=".env"):
    """
    Manually parse the .env file and return a dictionary of environment variables.

    Args:
        env_path (str): Path to the .env file.

    Returns:
        dict: Dictionary containing environment variables.
    """
    env_vars = {}

    if not os.path.exists(env_path):
        logger.warning(f"Warning: {env_path} not found. Continuing without it.")
        return env_vars

    with open(env_path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


def _main():
    """
    Spawns a Docker container to run the application inside Docker, passing necessary
    environment variables and mounting host paths.
    """
    logger.info(
        "Attempting to initializing a Docker container..."
    )
    if not is_docker_available():
        logger.error(
            "Docker is not installed or not running."
        )
        sys.exit(1)

    logger.info(
        "Checking Docker image..."
    )
    build_docker_image()

    # Prepare environment variables for Docker run
    env_file_path = os.path.abspath(".env")

    # Ensure the .env file exists
    if not os.path.exists(env_file_path):
        logger.error(f".env file not found at {env_file_path}")
        sys.exit(1)

    env_vars = load_env_file(".env")

    # The Docker command
    docker_cmd = [
        "docker", "run", "--rm", "-it",
        # So the code knows it's inside Docker
        "-e", "IN_DOCKER=1",
        # Pass environment variables to container
        "-e", f"OPENAI_API_KEY={env_vars.get(r'OPENAI_API_KEY')}",
        "-e", f"ANKI_CONNECT_URL={env_vars.get(r'ANKI_CONNECT_URL') or 'http://localhost:8765'}",
        "-e", r"INPUT_DIRECTORY=/app/content",
        "-e", r"ANKI_COLLECTION_MEDIA_PATH=/app/Anki-collection-media",
        "-e", r"PDF_VIEWER_MEDIA_PATH=/app/Ankifiles",
        # Mount the host's input directory to /app/content in container
        "-v", f"{env_vars.get(r'INPUT_DIRECTORY')}:/app/content",
        # Mount the host's Anki collection.media directory
        "-v", f"{env_vars.get(r'ANKI_COLLECTION_MEDIA_PATH')}:/app/Anki-collection-media",
        # Mount the host's Anki add-on 'pdf viewer' directory
        "-v", f"{env_vars.get(r'PDF_VIEWER_MEDIA_PATH')}:/app/Ankifiles",
        "flashcard-app",
        # Command inside the container:
        "python", "host.py"
    ]
    logger.info(
        "Restarting application within a docker container..."
    )
    result_code = subprocess.call(docker_cmd)
    sys.exit(result_code)


if __name__ == "__main__":
    _main()