import os
import io
import re
import sys
import json
import base64

from pdfminer.high_level import extract_text
from PIL import Image
from rich import print_json
from rich.pretty import Pretty, pprint
from rich.console import Console
from rich.markdown import Markdown
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI

from prompts import (
    TEXT_FORMAT,
    PLACEHOLDER_MESSAGE,
    REWRITE_PROMPT,
    CONCEPT_MAP_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    CONCEPTS_PROMPT,
    ABSENT_PROMPT,
    CHAIN_OF_THOUGHT,
    FLASHCARD_PROMPT,
)

# OpenAI Models
GPT_O1_PREVIEW = "o1-preview"
GPT_O1_MINI = "o1-mini"
GPT_4O = "gpt-4o"
GPT_4O_MINI = "gpt-4o-mini"
# Initialize the OpenAI client
client = OpenAI()
# Initialize Rich console for formatted output
console = Console()


class Concepts(BaseModel):
    chain_of_thought: str = Field(
        description="Think step by step to determine concept list items that are missing from the list and must be extracted from the source material."
    )
    concepts: List[str] = Field(
        description="A list of concept items cited verbatim from the source material and formatted in markdown.",
    )


class Front(BaseModel):
    chain_of_thought: str = Field(
        description=CHAIN_OF_THOUGHT
    )
    front: str = Field(
        description="A question formatted in markdown.",
    )

class Back(BaseModel):
    chain_of_thought: str = Field(
        description=CHAIN_OF_THOUGHT
    )
    back: str = Field(
        description="An answer formatted in markdown.",
    )

class Example(BaseModel):
    example: str = Field(
        description="An example that exists in the source material, reproduced verbatim, formatted in markdown."
    )

class Citation(BaseModel):
    citation: str = Field(
        description="The exact citation from the concepts list, formatted in markdown."
    )


class FlashcardItem(BaseModel):
    name: Literal[""]
    front: Front
    back: Back
    example: Example
    citation: Citation
    source: Literal[""]
    image: Literal[""]
    external_source: Literal[""]
    external_page: Literal[1]


class Flashcards(BaseModel):
    flashcards: List[FlashcardItem]


def detect_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.txt':
        return 'text'
    elif ext.lower() == '.pdf':
        return 'pdf'
    elif ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        return 'image'
    else:
        return 'unsupported'


def process_file(file_path, file_type):
    if file_type == 'text':
        with open(file_path, 'r', encoding='utf-8') as f:
            plain_text = f.read()
        return plain_text
    elif file_type == 'image':
        img = Image.open(file_path)
        img_uri = get_img_uri(img)
        return img_uri
    elif file_type == 'pdf':
        pdf_text = extract_text_from_doc(file_path)
        return pdf_text
    else:
        console.print(
            f"Unsupported file type: '{file_path}'.\n"
            "Supported file types are '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp'",
            style="red"
        )
        sys.exit(1)


def extract_text_from_doc(path):
    return extract_text(path)


def get_img_uri(img):
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_png}"


def get_completion(file_type, model, message_list, response_format):
    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=message_list,
            response_format=response_format,
            max_completion_tokens=4000,
            temperature=0,
            top_p=0.1,
        )
        finish_reason = completion.choices[0].finish_reason
        if finish_reason != "stop":
            console.print(
                f"Finished processing {file_type} with reason: {finish_reason}",
                style="yellow"
            )
        return completion
    except Exception as e:
        console.print(f"Error in processing {file_type}: ", Pretty(e, expand_all=True), style="red")
        sys.exit(1)



def handle_completion(system_message, user_message, response_format, file_type=None, file_contents=None):
    message_list = [{"role": "system", "content": system_message}]

    print_message("system", system_message, model=None, markdown=True)

    if file_type is not None and file_type.lower() == "image":
        model = GPT_4O
        content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{file_contents}"
                }
            }
        ]
        append_message("user", content, message_list)
        print_message("user", PLACEHOLDER_MESSAGE, model=None, markdown=True)
    elif system_message == REWRITE_PROMPT:
        model = GPT_4O_MINI
        append_message("user", file_contents, message_list)
        print_message("text", file_contents, model=None, markdown=False)
    else:
        model = GPT_4O_MINI
        append_message("user", user_message, message_list)
        print_message("user", user_message, model=None, markdown=True)


    completion = get_completion(
        file_type,
        model=model,
        message_list=message_list,
        response_format=response_format,
    )

    print_token_usage(completion)
    model = completion.model
    response = completion.choices[0].message.content

    if response_format is Flashcards:
        print_message("assistant", response, model, markdown=False)
    elif response_format is Concepts:
        print_message("assistant_list", response, model, markdown=False)
    else:
        print_message("assistant", response, model, markdown=True)

    return response


def print_message(role, content, model, markdown=False):
    role_styles = {
        "system": "[bold cyan]System Message",
        "user": "[bold green]User Message",
        "assistant": f"[bold yellow]{model}: Response",
        "assistant_list": f"[bold yellow]{model}: List Output",
        "token": "[bold magenta]Token Usage",
        "text": "[bold red]Text Extracted from File",
        "flashcard": "[bold red]Flashcard Item",
    }

    rule = role_styles.get(role.lower(), f"[bold]{role} Message")
    console.rule(rule)

    if role.lower() == "token":
        print("\n")
        pprint(content, expand_all=True)
        print("\n")
        return

    if role.lower() == "assistant_list":
        text_content = Concepts.model_validate_json(content)
        pprint(text_content)
        return

    if markdown and isinstance(content, str):
        console.print("\n", Markdown(content), "\n")
        return

    console.print("\n", content, "\n")


def print_token_usage(completion):
    print_message("token", completion.usage, model=None, markdown=False)


def append_message(role, response, messages):
    message = {"role": role.lower(), "content": response}
    messages.append(message)


def extract_markdown_title(markdown_text):
    # 1. ATX-style Header (e.g., # Title)
    atx_header_pattern = r'^\s{0,3}(#{1,6})\s+(.*?)\s*$'
    atx_match = re.search(atx_header_pattern, markdown_text, re.MULTILINE)
    if atx_match:
        # Extract the title without the '#' characters and surrounding spaces
        title = atx_match.group(2).strip()
        return title

    # 2. Setext-style Header (e.g., Title followed by ======)
    # Look for a line of text followed by a line of === or ---
    setext_header_pattern = r'^(?!#)([^\n]+)\n\s*([=-]{3,})\s*$'
    setext_match = re.search(setext_header_pattern, markdown_text, re.MULTILINE)
    if setext_match:
        # Extract the title from the first capturing group
        title = setext_match.group(1).strip()
        return title

    # 3. Plain Text: First non-empty line
    plain_text_pattern = r'^\s*(\S.*)$'
    plain_text_match = re.search(plain_text_pattern, markdown_text, re.MULTILINE)
    if plain_text_match:
        title = plain_text_match.group(1).strip()
        return title

    return ""


def parse_llm_response(response_str):
    try:
        data = json.loads(response_str)

        concepts = data.get("concepts", [])

        return concepts
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in parse_llm_response method: {e}")
        return [], []


def get_initial_prompt(file_type):
    if file_type.lower() == "image":
        return IMAGE_ANALYSIS_PROMPT
    else:
        return REWRITE_PROMPT


def main():
    if len(sys.argv) != 3:
        console.print("Usage: python generator.py <file_path> <file_name>", style="red")
        sys.exit(1)

    file_path = sys.argv[1]
    file_name = sys.argv[2]
    file_type = detect_file_type(file_path)
    file_contents = process_file(file_path, file_type)
    initial_prompt = get_initial_prompt(file_type)

    rewritten_text = handle_completion(initial_prompt, None, TEXT_FORMAT, file_type, file_contents)

    partial_concepts_list_response = handle_completion(CONCEPTS_PROMPT, rewritten_text, Concepts, file_type, file_contents)
    absent_prompt = ABSENT_PROMPT.format(SOURCE_MATERIAL=rewritten_text)
    final_concepts_list_response = handle_completion(absent_prompt, partial_concepts_list_response, Concepts, file_type, file_contents)

    concept_map_response = handle_completion(CONCEPT_MAP_PROMPT, rewritten_text, TEXT_FORMAT, file_type, file_contents)
    title = extract_markdown_title(concept_map_response)

    console.rule("[bold red] Final Concepts List")
    formatted_concepts_list = parse_llm_response(final_concepts_list_response)
    pprint(formatted_concepts_list)

    flashcard_prompt = FLASHCARD_PROMPT.format(concept_map=concept_map_response)
    flashcards_response = handle_completion(flashcard_prompt, final_concepts_list_response, Flashcards, file_type, file_contents)

    try:
        flashcards = Flashcards.model_validate_json(flashcards_response)
    except ValidationError as e:
        console.print("Error parsing flashcards:", style="red")
        console.print(str(e), style="red")
        sys.exit(1)

    for flashcard_item in flashcards.flashcards:
        flashcard_item.name = title
        flashcard_item.source = ""
        flashcard_item.external_source = file_name
        flashcard_item.image = file_name if file_type == "image" else ""

        # Flatten the fields:
        flashcard_item.front = flashcard_item.front.front
        flashcard_item.back = flashcard_item.back.back
        flashcard_item.example = flashcard_item.example.example
        flashcard_item.citation = flashcard_item.citation.citation

    print_message("flashcards", flashcards, model=None, markdown=False)


if __name__ == "__main__":
    main()