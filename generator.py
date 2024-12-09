import os
import sys
import io
import base64

from pdfminer.high_level import extract_text
from PIL import Image
from rich import print_json
from rich.pretty import Pretty
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI

from prompts import (
    TEXT_FORMAT,
    FLASHCARD_SCHEMA,
    PLACEHOLDER_MESSAGE,
    REWRITE_PROMPT,
    BRAINSTORM_KNOWLEDGE_MAP_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    BRAINSTORM_FLASHCARDS_PROMPT,
    JSON_FLASHCARDS_PROMPT,
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
        completion = client.chat.completions.create(
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
        console.print(f"Error in processing {file_type}: ", Pretty(e), style="red")
        sys.exit(1)



def handle_completion(file_type, system_message, response, file_contents, response_format):
    message_list = [{"role": "system", "content": system_message}]

    print_message("system", system_message, model=None, markdown=True)

    if file_type.lower() == "image":
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
        append_message("user", response, message_list)

        print_message("user", response, model=None, markdown=True)


    completion = get_completion(
        file_type,
        model=model,
        message_list=message_list,
        response_format=response_format,
    )

    print_token_usage(completion)
    model = completion.model
    response = completion.choices[0].message.content

    if response_format == FLASHCARD_SCHEMA:
        print_message("assistant", response, model, markdown=False)
    else:
        print_message("assistant", response, model, markdown=True)

    return response


def print_message(role, content, model, markdown=False):
    role_styles = {
        "system": "[bold cyan] System Message",
        "user": "[bold green]User Prompt (Source Material)",
        "assistant": f"[bold yellow]{model} Response",
        "token": "[bold magenta]Token Usage",
        "text": "[bold red]Text Extracted From PDF"
    }
    rule = role_styles.get(role.lower(), f"[bold]{role} Message")
    console.rule(rule)
    if markdown and role.lower() != "token":
        console.print("\n", Markdown(content), "\n")
    elif role.lower() == "token":
        console.print("\n", Pretty(content), "\n")
    elif role.lower() == "text":
        console.print("\n", content, "\n")
    else:
        print_json(content)


def append_message(role, response, messages):
    message = {"role": role.lower(), "content": response}
    messages.append(message)


def print_token_usage(completion):
    print_message("token", completion.usage, model=None, markdown=False)


def main():
    if len(sys.argv) != 2:
        console.print("Usage: python generator.py <file_path>", style="red")
        sys.exit(1)

    file_path = sys.argv[1]
    file_type = detect_file_type(file_path)
    file_contents = process_file(file_path, file_type)

    if file_type.lower() == "image":
        initial_prompt = IMAGE_ANALYSIS_PROMPT
    else:
        initial_prompt = REWRITE_PROMPT

    prompts = [
        (initial_prompt, TEXT_FORMAT),
        (BRAINSTORM_KNOWLEDGE_MAP_PROMPT, TEXT_FORMAT),
    ]

    response = None
    for system_message, response_format in prompts:
        response = handle_completion(file_type, system_message, response, file_contents, response_format)


if __name__ == "__main__":
    main()