"""
Purpose:

- Contains logger used across modules.
"""
import logging

# Configure the global logger here:
logging.basicConfig(
    level=logging.INFO,
    format="\n[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"  # Enhanced format for clarity
)

# Create and export a named logger to use across modules
logger = logging.getLogger("flashcard_app")

# Suppress logging from these third-party libraries to ERROR level
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('weasyprint.progress').setLevel(logging.ERROR)
logging.getLogger('markdown').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('fontTools.subset').setLevel(logging.ERROR)
logging.getLogger('fontTools.ttLib').setLevel(logging.ERROR)
