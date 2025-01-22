"""
Provides a globally configured logger for the flashcard application.

Highlights:
    - Sets a default logging level of INFO.
    - Defines a named logger ("flashcard_app") that other modules can import to log messages consistently.
    - Suppresses overly verbose logs from certain third-party libraries (e.g., WeasyPrint, fontTools).
    - Uses a custom log format including timestamps, logger names, and levels for clarity.
"""
import logging

# Configure the global logger settings:
#   - level=logging.INFO makes INFO (and above) messages visible.
#   - format includes timestamp, logger name, and log level.
logging.basicConfig(
    level=logging.INFO,
    format="\n[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"  # Enhanced format for clarity
)

# Instantiate and export a named logger to be reused throughout the codebase.
logger = logging.getLogger("flashcard_app")

# Reduce the logging verbosity of some third-party libraries to ERROR level
# to avoid cluttering logs with unnecessary information.
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('weasyprint.progress').setLevel(logging.ERROR)
logging.getLogger('markdown').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('fontTools.subset').setLevel(logging.ERROR)
logging.getLogger('fontTools.ttLib').setLevel(logging.ERROR)
