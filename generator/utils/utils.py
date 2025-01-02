"""
Purpose:

- Parsing LLM (Large Language Model) responses that are expected to be a JSON list of concepts,
- Printing messages to the console with color/styling using the `rich` library for debugging,
- Appending new messages to a conversation list.
"""
import json

from rich.markdown import Markdown
from rich.pretty import pprint
from rich.console import Console

from generator.utils.flashcard_logger import logger

console = Console()


def parse_concepts_list_response(response_str: str):
    """
    - Tries to `json.loads(...)` the string, returns a list of concepts if they exist.
    - Uses a `try/except` block to handle `json.JSONDecodeError`.
    """
    try:
        data = json.loads(response_str)
        return data.get("concepts", [])
    except json.JSONDecodeError as e:
        logger.error("Error parsing JSON in parse_concepts_list_response: %s", e)
        return []


def print_message(role, content, response_format, model, markdown):
    """
    - Uses `rich.console.Console` and the `Markdown` object to do pretty printing.
    - If `markdown=True`, it will render the content as Markdown.
    - If the role is "assistant" and `response_format` can parse the content, it tries to do so. Otherwise, it just prints.
    """
    role_styles = {
        "system": "[bold cyan]System Message",
        "user": "[bold green]User Message",
        "assistant": f"[bold yellow]{model}: Response" if model else "[bold yellow]Assistant",
        "token": "[bold magenta]Token Usage",
        "flashcard": "[bold orange]Flashcards",
        "problem_flashcards": "[bold red]Problem Flashcards",
    }
    rule = role_styles.get(role.lower(), f"[bold]{role} Message")
    console.rule(rule)

    # If content is Markdown text
    if markdown and isinstance(content, str):
        console.print("\n", Markdown(content), "\n")
        return

    # Token usage
    if role.lower() == "token":
        print("\n")
        pprint(content, expand_all=True)
        print("\n")
        return

    # If role is 'assistant' with a possible JSON content
    if role.lower() in ["assistant"]:
        if hasattr(response_format, "model_validate_json") and isinstance(content, str):
            try:
                text_content = response_format.model_validate_json(content)
                pprint(text_content)
                return
            except Exception:
                console.print("\n", content, "\n")
                return
        console.print("\n", content, "\n")
        return

    # For 'flashcard' or 'problem_flashcards', just pprint
    if role.lower() in ["flashcard", "problem_flashcards"]:
        pprint(content, expand_all=True)
        return

    # Default
    console.print("\n", content, "\n")


def append_message(role, response, messages):
    """
    - Creates a dict `{"role": role.lower(), "content": response}` and appends to `messages`; required by OpenAI completions API.
    - This is used for building a conversation to send to an LLM.
    """
    message = {"role": role.lower(), "content": response}
    messages.append(message)
