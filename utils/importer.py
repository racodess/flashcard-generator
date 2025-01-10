"""
Purpose:

- Communicates with the "AnkiConnect" Anki add-on (listens on port 8765),
- Adds newly generated flashcards ("notes" in Anki terminology) to the user’s Anki deck.
- Creates or updates "note" templates ("models" in AnkiConnect terminology) in Anki if needed,


**Important Note:**

- Requires Anki add-on "AnkiConnect":
    - A third-party API that exposes HTTP endpoints of Anki functionality (e.g. creating decks, adding notes).

- "AnkiConnect" Add-on requires Anki to be open on the user's system,
    - Otherwise, this application results in an error at the import step.
"""
import re
import html
import json
import urllib.request

from utils.flashcard_logger import logger
from utils import models, templates


def _request(action, **params):
    """
    - Convenience function that builds a dictionary in the format AnkiConnect expects:

     ```
     {
       "action": <action string>,
       "params": {...},
       "version": 6
     }
     ```

    :param action: The AnkiConnect action to perform.
    :param params: Additional parameters for the request.
    :return: A dictionary structured for use with AnkiConnect.
    """
    return {
        "action": action,
        "params": params,
        "version": 6
    }


def _invoke(action, **params):
    """
    - Actually sends the JSON request to `http://127.0.0.1:8765`, receives the response, checks for errors, and returns the “result.”

    :param action: The AnkiConnect action to perform.
    :param params: Additional parameters for the request.
    :return: The 'result' part of the AnkiConnect response.
    :raises Exception: If an error occurs or the response has unexpected fields.
    """
    request_json = json.dumps(_request(action, **params)).encode("utf-8")
    try:
        with urllib.request.urlopen(
            urllib.request.Request("http://127.0.0.1:8765", request_json)
        ) as response:
            data = json.load(response)
    except Exception as e:
        logger.error("Failed to communicate with AnkiConnect. Make sure the Anki application is open on this system: %s", e)
        raise

    if len(data) != 2:
        raise Exception("Response has an unexpected number of fields.")
    if "error" not in data:
        raise Exception("Response is missing required 'error' field.")
    if "result" not in data:
        raise Exception("Response is missing required 'result' field.")
    if data["error"] is not None:
        raise Exception(data["error"])

    return data["result"]


def ensure_template_exists(template_name):
    """
    - Checks if a “model” (Anki note type) with that name is in Anki. If not, calls `createModel` in AnkiConnect with your “Front” and “Back” HTML templates (for “Problem” or “Basic” flashcards).
    - This ensures Anki has the correct template before the flashcards are imported.

    :param template_name: The name of the Anki note type (model) to ensure.
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
        fields = templates.BASIC_TEMPLATE_FIELDS
        card_templates = [{
            "Name": "Front to Back",
            "Front": templates.BASIC_FRONT_TEMPLATE,
            "Back": templates.BASIC_BACK_TEMPLATE
        }]

    css = templates.BASIC_CSS

    _invoke(
        "createModel",
        modelName=template_name,
        inOrderFields=fields,
        cardTemplates=card_templates,
        css=css
    )

    logger.info("Anki note type '%s' created successfully.", template_name)


def create_deck(deck_name):
    """
    - Calls AnkiConnect’s `createDeck`. Anki automatically does nothing if that deck already exists, so it’s effectively an “ensure deck exists” method.

    :param deck_name: The name of the deck to create or ensure exists.
    :return: The result from AnkiConnect's createDeck action.
    """
    logger.info("Creating or ensuring existence of deck '%s'...", deck_name)
    return _invoke("createDeck", deck=deck_name)


def get_default_deck():
    """
    - Tries to find or create a deck that starts with `Imported`. If no `Imported` deck is found, it creates a new one like `Imported1`, `Imported2`, etc.
    - Each set of flashcards is imported to its own `Imported<num>` deck by default to allow the user an opportunity to curate the set before integrating it to their personal decks.

    :return: The name of the deck to use for imports.
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

    if imported_deck_numbers:
        next_deck_number = max(imported_deck_numbers) + 1
    else:
        next_deck_number = 1

    deck_name = f"Imported{next_deck_number}"
    create_deck(deck_name)
    logger.info("Importing flashcards to deck: %s", deck_name)
    return deck_name


def escape_html_entities(text):
    """
    Escape HTML entities in a string.

    :param text: The string to escape.
    :return: The escaped string.
    """
    return html.escape(text, quote=False)


def build_fields(fc, flashcards_model):
    """
    Construct and return a dict of fields for a single flashcard.
    The final dict is run once through HTML entity escaping, so we
    don't scatter repeated calls everywhere.
    """
    # 1) Start with common fields from fc.data
    fields = {
        "Image": fc.data.image,
        "external_source": fc.data.external_source,
        "external_page": str(fc.data.external_page),
        "url": fc.data.url
    }

    # 2) Branch for problem flashcards vs. general flashcards
    if isinstance(fc, models.ProblemFlashcardItem):
        fields["Header"] = fc.header
        fields["Problem"] = flashcards_model.problem
        fields["Problem_URL"] = flashcards_model.problem_url
        fields["Approach"] = fc.approach
        fields["Solution"] = fc.solution

        for i, step in enumerate(fc.steps):
            fields[f"Step {i+1}"] = step.step
            fields[f"Code {i+1}"] = step.code
            fields[f"Pitfall {i+1}"] = step.pitfall

        fields["Time"] = fc.time
        fields["Time Explanation"] = fc.time_explanation
        fields["Space"] = fc.space
        fields["Space Explanation"] = fc.space_explanation

    else:
        # e.g. ConceptFlashcardItem or something else
        fields["Header"] = flashcards_model.header
        fields["Front"] = fc.front
        fields["Back"] = fc.back
        fields["Example"] = fc.example

    # 3) Now apply HTML escaping to every field in one pass
    escaped_fields = {k: escape_html_entities(v) for k, v in fields.items()}
    return escaped_fields


def get_notes(flashcards_model, template_name, deck_name):
    """
    - Converts your internal Pydantic model (`Flashcard`, `ProblemFlashcard`, etc.)
      to the format Anki expects.
    - Returns a tuple of (notes, deck_name).
    """
    ensure_template_exists(template_name)

    if deck_name is None:
        deck_name = get_default_deck()

    notes = []
    for fc in flashcards_model.flashcards:
        fields = build_fields(fc, flashcards_model)

        note = {
            "deckName": deck_name,
            "modelName": template_name,
            "fields": fields,
            "options": {"allowDuplicate": True},
            "tags": fc.tags
        }
        notes.append(note)

    return notes, deck_name


def add_flashcards_to_anki(flashcards_model, template_name="Default", deck_name=None):
    """
    The culminating function that:

    1. Calls `get_notes(...)` to build a list of notes from the flashcards data,
    2. Then calls `_invoke("addNotes", notes=notes)` to push them into Anki.

    - If some notes fail, logs that info.
    - Duplicate notes are allowed by default due to Anki flagging the "note types" created by this application as having duplicate fields, which is intentional but erroneous behavior.

    :param flashcards_model: The flashcards model to add.
    :param template_name: The name of the Anki note type (model) to use.
    :param deck_name: The name of the deck to place notes in.
    """
    notes, deck_name = get_notes(flashcards_model, template_name, deck_name)
    result = _invoke("addNotes", notes=notes)

    if result:
        # If note_id is None in the response, it means adding that note failed.
        failed_notes = [i for i, note_id in enumerate(result) if note_id is None]
        if not failed_notes:
            logger.info("Successfully added %d notes to deck '%s'.", len(result), deck_name)
        else:
            logger.warning("Failed to add %d notes to deck '%s'.", len(failed_notes), deck_name)
    else:
        logger.error("Failed to add notes to Anki.")

    logger.info("Notes added with IDs: %s", result)
