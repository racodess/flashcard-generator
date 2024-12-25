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


def escape_html_entities(text):
    text = html.escape(text, quote=False)
    return text


def add_flashcards_to_anki(flashcards_model, template_name="Default", deck_name="Default"):
    ensure_template_exists(template_name)

    notes = []
    for fc in flashcards_model.flashcards:
        fields = {
            "Header": fc.title,
            "Image": fc.image,
            "external_source": fc.external_source,
            "external_page": str(fc.external_page),
        }

        if isinstance(fc, models.ProblemFlashcardItem):
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
            fields["Front"] = fc.front,
            fields["Back"] = fc.back,
            fields["Example"] = fc.example,

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

    result = invoke("addNotes", notes=notes)
    console.log("Notes added with IDs:", result)