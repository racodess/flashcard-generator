import logging

# Configure the global logger here:
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Create and export a named logger to use across modules
logger = logging.getLogger("flashcard_app")
