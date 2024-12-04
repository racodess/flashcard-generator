import os
import sys
import io
import base64
import json

from pdf2image import convert_from_path
from PIL import Image
from rich import print_json
from rich.text import Text
from rich.pretty import Pretty
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI

from prompts import (
    TEXT,
    FLASHCARD_SCHEMA,
    SYSTEM_MESSAGE,
    INITIAL_PROMPT_IMG,
    INITIAL_PROMPT_TEXT,
    FRONT_BACK_PROMPT,
    WORDINESS_PROMPT,
    FIND_EXAMPLES_PROMPT,
    ADD_EXAMPLES_PROMPT,
    CITATIONS_PROMPT,
    REMOVE_BAD_QUESTIONS_PROMPT,
)

# OpenAI Models
GPT_O1_PREVIEW = "o1-preview"
GPT_O1_MINI = "o1-mini"
GPT_4O = "gpt-4o"
GPT_4O_MINI = "gpt-4o-mini"

# Use this model
MODEL = GPT_4O_MINI

# Initialize the OpenAI client
client = OpenAI()

# Initialize Rich console for formatted output
console = Console()


def detect_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.txt':
        return 'text'
    elif ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf']:
        return 'image'
    else:
        return 'unsupported'


def process_file(file_path, file_type):
    if file_type == 'text':
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        initial_prompt = INITIAL_PROMPT_TEXT.format(TEXT=content)
        img_uri = None
    elif file_type == 'image':
        if file_path.lower().endswith('.pdf'):
            images = convert_doc_to_images(file_path)
            img_uri = get_img_uri(images[0])
        else:
            img = Image.open(file_path)
            img_uri = get_img_uri(img)
        initial_prompt = INITIAL_PROMPT_IMG
    else:
        console.print(
            f"Unsupported file type: '{file_path}'.\n"
            "Supported file types are '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf'",
            style="red"
        )
        sys.exit(1)
    return initial_prompt, img_uri


def convert_doc_to_images(path):
    return convert_from_path(path)


def get_img_uri(img):
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_png}"


def analyze_image(img_uri, message_list):
    messages = message_list.copy()
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": img_uri}
                }
            ]
        }
    )

    try:
        completion = client.chat.completions.create(
            model=GPT_4O,
            messages=messages,
            max_tokens=1000,
            temperature=0,
            top_p=0.1
        )
        return completion
    except Exception as e:
        console.print(f"Error while analyzing image: {e}", style="red")
        sys.exit(1)


def get_completion(model, prompt, response_format, message_list):

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=message_list,
            response_format=response_format,
            max_tokens=16383,
            temperature=0,
            top_p=0.1,
        )
        return completion
    except Exception as e:
        console.print(f"Error while generating response: {e}", style="red")
        sys.exit(1)


def print_user_message(message, markdown):
    if markdown:
        md = Markdown(message)
        console.rule("[bold green]User Prompt")
        console.print(f"\n\n", md, "\n")
    else:
        console.print(f"\n\n{message}\n")

def print_model_response(model, response, markdown):
    if markdown is True:
        md = Markdown(response)
        console.rule(f"[bold yellow]{model} Response")
        console.print(f"\n\n", md, "\n")
    else:
        console.rule(f"[bold yellow]{model} Response")
        print_json(response)

def print_token_usage(completion):
    console.rule(f"[bold magenta]Token Usage")
    console.print(f"\n", Pretty(completion.usage), "\n")

def append_user_prompt(prompt_text, message_list):
    message_list.append({"role": "user", "content": prompt_text})

def append_model_response(response, message_list):
    message_list.append({"role": "assistant", "content": response})


def main():
    if len(sys.argv) != 2:
        console.print("Usage: python generator.py <file_path>", style="red")
        sys.exit(1)

    file_path = sys.argv[1]
    file_type = detect_file_type(file_path)
    initial_prompt, img_uri = process_file(file_path, file_type)

    message_list = [SYSTEM_MESSAGE]

    prompts = [
        ("Initial Prompt", initial_prompt, TEXT),
        ("Front and Back Prompt", FRONT_BACK_PROMPT, FLASHCARD_SCHEMA),
        ("Wordiness Prompt", WORDINESS_PROMPT, FLASHCARD_SCHEMA),
        ("Find Examples Prompt", FIND_EXAMPLES_PROMPT, TEXT),
        ("Add Examples Prompt", ADD_EXAMPLES_PROMPT, FLASHCARD_SCHEMA),
        ("Citations Prompt", CITATIONS_PROMPT, FLASHCARD_SCHEMA),
        ("Remove Bad Questions Prompt", REMOVE_BAD_QUESTIONS_PROMPT, FLASHCARD_SCHEMA),
    ]

    for title, prompt_text, response_format in prompts:
        print_user_message(prompt_text, markdown=True)
        if title == "Initial Prompt" and initial_prompt == INITIAL_PROMPT_IMG:
            completion = analyze_image(img_uri, message_list)
            append_user_prompt("See assistant's presentation below:", message_list)
        else:
            append_user_prompt(prompt_text, message_list)
            completion = get_completion(MODEL, prompt_text, response_format, message_list)
        print_token_usage(completion)
        response = completion.choices[0].message.content
        append_model_response(response, message_list)
        if response_format == FLASHCARD_SCHEMA:
            print_model_response(MODEL, response, markdown=False)
        else:
            print_model_response(MODEL, response, markdown=True)


if __name__ == "__main__":
    main()