import os
import sys
import argparse
import subprocess

from utils.flashcard_logger import logger


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


def is_inside_docker():
    """
    Simple check to see if we are *inside* a Docker container.
    """
    # Check environment variable or the standard /.dockerenv file
    if os.getenv("IN_DOCKER") == "1":
        return True
    if os.path.exists("/.dockerenv"):
        return True
    return False


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


def main():
    """
    Main CLI entry point. Decides if we run on host or in Docker.

    The order of logic is:
      1. Parse CLI for --run-mode.
      2. If run-mode = 'host'  -> run_on_host().
      3. If run-mode = 'docker'-> run_in_docker().
      4. If no run-mode is specified:
            - Check if inside Docker: if yes, run_on_host().
            - Else if Docker is installed: run_in_docker().
            - Else run_on_host().
    """
    args = parse_arguments()

    # Optional: ensure .env file exists, or warn/fail as needed
    env_file_path = os.path.abspath(".env")
    if not os.path.exists(env_file_path):
        logger.error(f".env file not found at {env_file_path}.")
        sys.exit(1)

    if args.run_mode == "host":
        # Run the "host" logic directly
        subprocess.call([sys.executable, "host.py"])
    elif args.run_mode == "docker":
        # Spin up a Docker container
        subprocess.call([sys.executable, "container.py"])
    else:
        # No run-mode specified
        if is_inside_docker():
            # If we are already in Docker, run on host.
            subprocess.call([sys.executable, "host.py"])
        else:
            # We are on the host
            if is_docker_available():
                # Docker is installed -> default to Docker
                subprocess.call([sys.executable, "container.py"])
            else:
                # Docker not installed or not running -> fallback to host
                subprocess.call([sys.executable, "host.py"])


if __name__ == "__main__":
    main()
