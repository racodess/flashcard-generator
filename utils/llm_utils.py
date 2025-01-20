"""
LLM utility functions.
"""
import ast
from enum import Enum

from docstring_parser.attrdoc import ast_is_literal_str
from rich.console import Console
from openai import OpenAI
from rich.markdown import Markdown
from rich.pretty import pprint
from weasyprint.css.validation.properties import content

from utils import prompts, models
from utils.flashcard_logger import logger

console = Console()
client = OpenAI()

class PromptType(Enum):
    REWRITE_TEXT = "rewrite_text"
    CONCEPTS = "concepts"
    PROBLEM_SOLVING = "problem_solving"

PROMPT_TEMPLATES = {
    PromptType.REWRITE_TEXT: prompts.REWRITE_PROMPT,
    PromptType.CONCEPTS: prompts.CONCEPT_FLASHCARD_PROMPT,
    PromptType.PROBLEM_SOLVING: prompts.PROBLEM_FLASHCARD_PROMPT,
}


def get_system_message(
        prompt_type: PromptType,
        **kwargs
) -> str:
    template = PROMPT_TEMPLATES.get(prompt_type, "")
    return template.format(**kwargs)


def get_rewrite(content, content_type):
    system_message = get_system_message(
        PromptType.REWRITE_TEXT
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": content}
    ]
    completion = _get_completion(
        messages=messages,
        run_as_image=(content_type not in ["text", "url"]),
        response_format=models.TEXT_FORMAT,
    )
    response = completion.choices[0].message.content
    return response


def get_flashcards(
        conversation,
        system_message,
        user_text,
        run_as_image,
        response_format
):
    if not conversation:
        conversation.append({"role": "system", "content": system_message})

    messages = []
    if run_as_image:
        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{user_text}"
                        }
                    }
                ]
            }
        ]
        conversation.append({"role": "user", "content": "Image placeholder for brevity."})
    else:
        conversation.append({"role": "user", "content": user_text})

    completion = _get_completion(
        messages=messages if run_as_image else conversation,
        run_as_image=run_as_image,
        response_format=response_format
    )
    response = completion.choices[0].message.content

    conversation.append({"role": "assistant", "content": response})

    for item in conversation:
        for k, v in item.items():
            if k == "role":
                console.log(f"\n[bold red]{k}:[/bold red]", v)
            else:
                console.log(f"[bold red]{k}:[/bold red]\n", v)

    if len(conversation) > 4:
        del conversation[1:3]

    console.log("\n[bold red]Token Usage:[/bold red]", completion.usage)

    return response


def _get_completion(
    messages: list,
    response_format,
    run_as_image: bool = False
):
    gpt_4o = "gpt-4o-2024-08-06"
    gpt_4o_mini = "gpt-4o-mini"
    model = gpt_4o if run_as_image else gpt_4o_mini

    console.log(f"\n[bold cyan]Messages sent to `{model}`:[/bold cyan]\n", messages)

    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_format,
            max_completion_tokens=16384,
            temperature=0,
            top_p=0.1,
        )
    except Exception as e:
        logger.error("Error calling LLM: %s", e, exc_info=True)
        raise

    console.log(f"\n[bold yellow]`{model}` response:[/bold yellow]\n", completion.choices[0].message.content)

    return completion
