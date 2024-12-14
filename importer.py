import json
import urllib.request
from rich.console import Console
from rich.pretty import pprint

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

def ensure_model_exists():
    model_name = "AnkiConnect: Test"

    # Check if model already exists
    existing_models = invoke("modelNames")
    if model_name in existing_models:
        console.log(f"Model '{model_name}' already exists.")
        return

    console.log(f"Model '{model_name}' not found. Creating it...")

    # Define the fields in order
    fields = [
        "Name",
        "Front",
        "Back",
        "Example",
        "Image",
        "external_source",
        "external_page"
    ]

    # Define the templates
    # From the snippet: qfmt is the "Front" template and afmt is the "Back" template for createModel
    front_template = """<link rel="stylesheet" type="text/css" href="_prism.css">
<script src="_prism.js"></script>

<u><strong>{{Name}}</strong></u>
<br>
<br>
<div class='container'><div>{{Front}}</div></div>
"""
    back_template = """{{FrontSide}}

<hr id=answer>

<br>
<div class='container'><div>{{Back}}</div></div>

<br>
<br>

{{#Example}}
<br>
<br>
{{Example}}
<div class='container'><div>{{Example}}</div></div>
{{/Example}}

{{#Image}}
<br>
<br>
<img src="{{Image}}" />
{{/Image}}

{{#external_source}}
<br>
<br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

    card_templates = [{
        "Name": "Card 1",
        "Front": front_template,
        "Back": back_template
    }]

    # CSS from snippet
    css = """.card {
    font-family: arial;
    font-size: 16px;
    line-height: 1.5;
    text-align: center;
    color: black;
    background-color: white;
}

@media (max-width: 767px) {
    .card {
        font-size: 12px;
    }
}

pre:has(code),
table:has(.highlight),
.inline {
    width: auto;
    overflow: auto;
    box-sizing: border-box;
}

pre:has(code),
div.highlight,
.inline {
    padding: 10px;
    border: 1px solid;
    border-radius: 10px;
    border-color: DarkGray;
}

.inline {
    font-family: monospace;
    background-color: #ecf0f1;
}

li {
    margin-top: 10px;
}

code {
    padding-left: 3px;
    padding-right: 3px;
    margin-left: 2px;
    margin-right: 2px;
    border-radius: 3px;
    background-color: #ecf0f1;
    font-family: monospace;
    font-weight: 500;
}

.container {
    display: flex;
    justify-content: center;
}

.ex-break {
    width: 50%;
}
"""

    # Invoke createModel
    invoke("createModel", modelName=model_name, inOrderFields=fields, cardTemplates=card_templates, css=css)

    console.log(f"Model '{model_name}' created successfully.")


# Example usage:
if __name__ == "__main__":
    ensure_model_exists()
    # After ensuring the model, you'd proceed to add your cards using similar invoke calls.