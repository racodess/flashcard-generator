"""
Purpose:

- Communicates with the "AnkiConnect" Anki add-on (listens on port 8765),
- Adds newly generated flashcards ("notes" in Anki terminology) to the user’s Anki deck,
- Ensures that the proper note types ("models") exist in Anki before adding notes.

AnkiConnect details:
    - Anki must be open, with the AnkiConnect add-on installed and active (by default on port 8765).
    - If Anki is not running or AnkiConnect is not installed, requests will fail.

Typical usage:
    1. Provide a `flashcards_model` containing all your flashcards.
    2. Optionally specify a `template_name` (e.g., "AnkiConnect: Problem") and `deck_name`.
    3. If the note template does not exist in Anki, this script creates it.
    4. If the deck does not exist, it is created (or a default is used).
    5. The flashcards are then sent to Anki via JSON requests over HTTP.

Error handling:
    - If communication with AnkiConnect fails, an error is logged, and the exception is raised.
    - If any note fails to be added (returns None from AnkiConnect), a warning is logged,
      but the process continues for the remaining notes.
"""
import os
import re
import html
import json
import urllib.request

from rich.console import Console

from utils.flashcard_logger import logger
from utils import models, templates

console = Console()


def anki_import(
        flashcards_model,
        template_name="Default",
        deck_name=None
):
    """
    Primary entry point for pushing flashcards into Anki.

    Steps:
      1. Transforms the flashcards into a list of notes via `_get_notes(...)`.
      2. Sends those notes to AnkiConnect with the "addNotes" action.
      3. Logs the result of the import.

    Behavior:
      - If any notes fail to be added (AnkiConnect returns None for their ID),
        a warning is logged.
      - Duplicate checks are disabled by setting "allowDuplicate": True
        because some note types used by this application might have repeated fields.

    Args:
        flashcards_model (BaseModel): A Pydantic model instance containing flashcards.
        template_name (str, optional): Name of the Anki note type (model) to use. Defaults to "Default".
        deck_name (str, optional): Name of the Anki deck for storing the notes. If None, a default deck is used.

    Returns:
        None
    """
    notes, deck_name = _get_notes(
        flashcards_model,
        template_name,
        deck_name
    )
    result = _invoke(
        "addNotes",
        notes=notes
    )

    # Check if any notes failed to add (None in the result array)
    if result:
        failed_notes = [i for i, note_id in enumerate(result) if note_id is None]
        if not failed_notes:
            logger.info("Successfully added %d notes to deck '%s'.", len(result), deck_name)
        else:
            logger.warning("Failed to add %d notes to deck '%s'.", len(failed_notes), deck_name)
    else:
        logger.error("Failed to add notes to Anki.")

    logger.info("Notes added with IDs: %s", result)


def _request(action, **params):
    """
    Builds a JSON-compatible dictionary that AnkiConnect expects for a given action.

    The structure follows the AnkiConnect specification:
      {
        "action": <action string>,
        "params": {...},
        "version": 6
      }

    Args:
        action (str): The AnkiConnect action to perform (e.g., "createDeck", "addNotes").
        **params: Arbitrary additional named parameters required by the action.

    Returns:
        dict: A dictionary ready to be converted to JSON and sent to AnkiConnect.
    """
    return {
        "action": action,
        "params": params,
        "version": 6
    }


def _invoke(action, **params):
    """
    Sends a request to AnkiConnect's HTTP endpoint (http://127.0.0.1:8765).

    If you run this application locally, you can set ANKI_CONNECT_URL=http://127.0.0.1:8765.

    If you run with Docker on:
    - Windows/macOS: you can set it to http://host.docker.internal:8765
    - Linux with --net=host: you can keep it at http://127.0.0.1:8765.

    Steps:
      1. Converts the action and params into JSON.
      2. Sends an HTTP POST request to AnkiConnect.
      3. Parses the response JSON.
      4. Checks for errors in the response (raises an exception if found).
      5. Returns the 'result' field of the response.

    Args:
        action (str): An AnkiConnect action name (e.g., "modelNames", "addNotes").
        **params: Key-value pairs that get passed along as parameters.

    Raises:
        Exception: If the response format is unexpected or if the 'error' field is non-null.

    Returns:
        Any: The 'result' portion of the response JSON, which can be various data types.
    """
    anki_connect_url = os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765")

    request_json = json.dumps(_request(action, **params)).encode("utf-8")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(anki_connect_url, request_json)
        ) as response:
            data = json.load(response)
    except Exception as e:
        logger.error(
            "Failed to communicate with AnkiConnect at %s. Make sure Anki is open and AnkiConnect is installed: %s",
            anki_connect_url, e
        )
        raise

    # Validate the response structure
    if len(data) != 2:
        raise Exception("Response has an unexpected number of fields.")
    if "error" not in data:
        raise Exception("Response is missing required 'error' field.")
    if "result" not in data:
        raise Exception("Response is missing required 'result' field.")

    # If 'error' is non-null, there's an issue that must be raised
    if data["error"] is not None:
        raise Exception(data["error"])

    return data["result"]


def _has_template(template_name):
    """
    Ensures that the specified Anki note type ('model') exists. If it doesn't, creates it.

    - Calls AnkiConnect's "modelNames" action to list existing note types.
    - If the `template_name` isn't found, builds a request to "createModel".
    - The structure of fields and card templates differs for "Problem" versus "Basic" note types.
    - Also applies a default CSS stored in `templates.BASIC_CSS`.

    Args:
        template_name (str): The Anki model name (e.g., "AnkiConnect: Problem").
    """
    existing_models = _invoke("modelNames")
    if template_name in existing_models:
        logger.info("Anki note type '%s' already exists.", template_name)
        return

    logger.info("Anki note type '%s' not found. Creating it...", template_name)

    if template_name == templates.PROBLEM_CARD_NAME:
        fields = templates.PROBLEM_TEMPLATE_FIELDS
        card_templates = [
            {
                "Name": "Approach",
                "Front": templates.PROBLEM_APPROACH_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_APPROACH_BACK_TEMPLATE
            },
            {
                "Name": "Time and Space",
                "Front": templates.PROBLEM_TIME_SPACE_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_TIME_SPACE_BACK_TEMPLATE
            },
            {
                "Name": "Step 1",
                "Front": templates.PROBLEM_STEP1_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP1_BACK_TEMPLATE
            },
            {
                "Name": "Step 2",
                "Front": templates.PROBLEM_STEP2_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP2_BACK_TEMPLATE
            },
            {
                "Name": "Step 3",
                "Front": templates.PROBLEM_STEP3_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP3_BACK_TEMPLATE
            },
            {
                "Name": "Step 4",
                "Front": templates.PROBLEM_STEP4_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP4_BACK_TEMPLATE
            },
            {
                "Name": "Step 5",
                "Front": templates.PROBLEM_STEP5_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP5_BACK_TEMPLATE
            },
            {
                "Name": "Step 6",
                "Front": templates.PROBLEM_STEP6_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP6_BACK_TEMPLATE
            },
            {
                "Name": "Step 7",
                "Front": templates.PROBLEM_STEP7_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP7_BACK_TEMPLATE
            },
            {
                "Name": "Step 8",
                "Front": templates.PROBLEM_STEP8_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP8_BACK_TEMPLATE
            },
            {
                "Name": "Step 9",
                "Front": templates.PROBLEM_STEP9_FRONT_TEMPLATE,
                "Back": templates.PROBLEM_STEP9_BACK_TEMPLATE
            },
        ]
    else:
        # For a basic card template, only a single front-back format is created
        fields = templates.BASIC_TEMPLATE_FIELDS
        card_templates = [{
            "Name": "Front to Back",
            "Front": templates.BASIC_FRONT_TEMPLATE,
            "Back": templates.BASIC_BACK_TEMPLATE
        }]

    css = templates.BASIC_CSS

    # Send request to create the model
    _invoke(
        "createModel",
        modelName=template_name,
        inOrderFields=fields,
        cardTemplates=card_templates,
        css=css
    )

    logger.info("Anki note type '%s' created successfully.", template_name)


def _get_deck(deck_name):
    """
    Ensures that the specified deck exists in Anki.

    It calls AnkiConnect's "createDeck" action with the given name:
      - If the deck doesn't exist, it is created.
      - If it already exists, Anki does nothing.

    Args:
        deck_name (str): The name of the deck to create or ensure exists.

    Returns:
        Any: The result from the AnkiConnect call, often an integer representing the deck ID.
    """
    logger.info("Creating or ensuring existence of deck '%s'...", deck_name)
    return _invoke("createDeck", deck=deck_name)


def _get_default_deck():
    """
    Obtains a default 'ImportedX' deck name for storing newly imported flashcards.

    Logic:
      1. Retrieves the list of existing decks from Anki (`deckNames`).
      2. Looks for decks matching the pattern "Imported<number>" (case-insensitive).
      3. Finds the maximum deck number in that pattern, increments by 1, and uses it.
      4. If none exist, starts from "Imported1".

    This approach ensures that each import goes to a fresh deck,
    allowing users to reorganize or rename decks later.

    Returns:
        str: The deck name, e.g. "Imported2".
        If deck names could not be retrieved, logs a warning and returns None.
    """
    existing_decks = _invoke("deckNames")
    if not existing_decks:
        logger.warning("Failed to retrieve deck names from Anki.")
        return None

    imported_deck_pattern = re.compile(r"^Imported(\d+)$", re.IGNORECASE)
    imported_deck_numbers = []
    for deck in existing_decks:
        match = imported_deck_pattern.match(deck)
        if match:
            imported_deck_numbers.append(int(match.group(1)))

    # Determine the next Imported deck number
    if imported_deck_numbers:
        next_deck_number = max(imported_deck_numbers) + 1
    else:
        next_deck_number = 1

    deck_name = f"Imported{next_deck_number}"
    # Ensure the deck actually exists in Anki
    _get_deck(deck_name)
    logger.info("Importing flashcards to deck: %s", deck_name)
    return deck_name


def _get_fields(fc, flashcards_model):
    """
    Builds a dictionary of field data for a single flashcard, conforming to the note model.

    General logic:
      - Populate common fields (Image, external_source, etc.).
      - If it's a ProblemFlashcardItem, add problem-specific fields (Approach, Steps, etc.).
      - If it's a ConceptFlashcardItem, add front/back/example fields.
      - Escape HTML entities in each field to avoid formatting conflicts in Anki.

    Args:
        fc (Union[ProblemFlashcardItem, ConceptFlashcardItem]): A single flashcard object.
        flashcards_model (Union[ProblemFlashcard, Flashcard]): The top-level flashcard model containing shared data.

    Returns:
        dict: A mapping of Anki field names -> string content, ready for insertion.
    """
    # Basic fields shared among card types
    fields = {
        "Image": fc.data.image,
        "external_source": fc.data.external_source,
        "external_page": str(fc.data.external_page),
        "url": fc.data.url
    }

    # Distinguish between problem flashcards and concept flashcards
    if isinstance(fc, models.ProblemFlashcardItem):
        # Problem-specific fields
        fields["Header"] = fc.header
        fields["Problem"] = flashcards_model.problem
        fields["Problem_URL"] = flashcards_model.problem_url
        fields["Approach"] = fc.approach
        fields["Solution"] = fc.solution

        for i, step in enumerate(fc.steps):
            # Dynamically name the Step, Code, and Pitfall fields
            fields[f"Step {i+1}"] = step.step
            fields[f"Code {i+1}"] = step.code
            fields[f"Pitfall {i+1}"] = step.pitfall

        fields["Time"] = fc.time
        fields["Time Explanation"] = fc.time_explanation
        fields["Space"] = fc.space
        fields["Space Explanation"] = fc.space_explanation
    else:
        # ConceptFlashcardItem fields
        fields["Header"] = flashcards_model.header
        fields["Front"] = fc.front
        fields["Back"] = fc.back
        fields["Example"] = fc.example

    # Escape HTML in all fields to avoid formatting issues in Anki
    escaped_fields = {
        k: html.escape(v, quote=False) for k, v in fields.items()
    }
    return escaped_fields


def _get_notes(
        flashcards_model,
        template_name,
        deck_name
):
    """
    Converts a flashcards model into a list of Anki-compatible "notes",
    also ensuring the proper template and deck exist in Anki.

    Steps:
      1. Calls `_has_template(template_name)` to ensure Anki has the needed note type.
      2. Determines or creates the deck (either a user-specified name or an 'ImportedX' default).
      3. Iterates over the flashcards in the model, converting each into a dict suitable
         for AnkiConnect's "addNotes" action.

    Args:
        flashcards_model (BaseModel): The Pydantic model holding the flashcards.
        template_name (str): The Anki note type name (modelName).
        deck_name (str): The deck name to use. If None, a default is retrieved/created.

    Returns:
        tuple: (notes, deck_name) where
            - notes is a list of dictionaries representing Anki notes,
            - deck_name is the resolved deck name used.
    """
    # Confirm that the desired note type (model) is present in Anki
    _has_template(template_name)
    deck_name = deck_name or _get_default_deck()

    notes = []
    # Convert each flashcard in the model to an Anki note format
    for fc in flashcards_model.flashcards:
        notes.append(
            {
                "deckName": deck_name,
                "modelName": template_name,
                "fields": _get_fields(fc, flashcards_model),
                "options": {"allowDuplicate": True},
                "tags": fc.tags
            }
        )
    return notes, deck_name
