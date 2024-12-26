import re
import html
import json
import models
import templates
import urllib.request
from rich.console import Console

console = Console()

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    request_json = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(
        urllib.request.Request('http://127.0.0.1:8765', request_json)
    ))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def ensure_template_exists(template_name):
    existing_models = invoke("modelNames")

    if template_name in existing_models:
        console.log(f"Model '{template_name}' already exists.")
        return

    console.log(f"Model '{template_name}' not found. Creating it...")

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

    invoke("createModel", modelName=template_name, inOrderFields=fields, cardTemplates=card_templates, css=css)

    console.log(f"Model '{template_name}' created successfully.")


def create_deck(deck_name):
    return invoke("createDeck", deck=deck_name)


def get_default_deck():
    existing_decks = invoke("deckNames")

    if not existing_decks:
        console.log("Failed to retrieve deck names from Anki.")
        return

    imported_deck_pattern = re.compile(r'^Imported(\d+)$', re.IGNORECASE)
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

    console.log(f"Importing flashcards to deck: {deck_name}")

    return deck_name


def escape_html_entities(text):
    text = html.escape(text, quote=False)
    return text


def get_notes(flashcards_model, template_name, deck_name):
    ensure_template_exists(template_name)

    if deck_name is None:
        deck_name = get_default_deck()
    else:
        deck_name = deck_name

    notes = []
    for fc in flashcards_model.flashcards:
        fields = {
            "Image": fc.data.image,
            "external_source": fc.data.external_source,
            "external_page": str(fc.data.external_page),
        }
        if isinstance(fc, models.ProblemFlashcardItem):
            fields["Header"] = fc.header
            fields["Problem"] = flashcards_model.problem
            fields["URL"] = flashcards_model.url
            fields["Approach"] = fc.approach
            fields["Solution"] = escape_html_entities(fc.solution)

            for i, step in enumerate(fc.steps):
                fields[f"Step {i + 1}"] = step.step
                fields[f"Code {i + 1}"] = escape_html_entities(step.code)
                fields[f"Pitfall {i + 1}"] = step.pitfall

            fields["Time"] = fc.time
            fields["Time Explanation"] = fc.time_explanation
            fields["Space"] = fc.space
            fields["Space Explanation"] = fc.space_explanation
        else:
            fields["Header"] = flashcards_model.header
            fields["Front"] = fc.front
            fields["Back"] = fc.back
            fields["Example"] = fc.example

        note = {
            "deckName": deck_name,
            "modelName": template_name,
            "fields": fields,
            "options": {
                "allowDuplicate": True
            },
            "tags": fc.tags
        }
        notes.append(note)

    return notes


def add_flashcards_to_anki(flashcards_model, template_name="Default", deck_name=None):
    notes = get_notes(flashcards_model, template_name, deck_name)

    result = invoke("addNotes", notes=notes)

    if result:
        if all(note_id is not None for note_id in result):
            console.log(f"Successfully added {len(result)} notes to deck '{deck_name}'.")
        else:
            failed_notes = [i for i, note_id in enumerate(result) if note_id is None]
            console.log(f"Failed to add {len(failed_notes)} notes to deck '{deck_name}'.")
    else:
        console.log("Failed to add notes to Anki.")

    console.log("Notes added with IDs:", result)