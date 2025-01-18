"""
Purpose:

- LLM utility functions:
    - Decide which OpenAI LLM to call
    - Build the “system” and “user” messages for the LLM
    - Handle structured responses using OpenAI API
"""
from enum import Enum

from rich.console import Console

from utils import format_utils, prompts
from utils.flashcard_logger import logger

from openai import OpenAI

"""
OpenAI LLM references:

- GPT-4o:
    - Currently used for image analysis,
    - Handles images in a reasonable amount of tokens,
    - Processing many images can result in high-costs,
    - Moderate cost overall,
    - Moderate-quality (sometimes stubborn low-quality) output.

- GPT-4o-mini: 
    - Currently used for text,
    - Uses x33 the amount of tokens compared to GPT-4o for images at an overall slightly higher cost,
    - Cheapest,
    - Fastest,
    - Good-quality output.
"""

console = Console()
client = OpenAI()

convo_hist = []


class PromptType(Enum):
    """
    - The different types of LLM prompts,
    - Defined in `prompts.py`.
    """
    REWRITE_TEXT = "rewrite_text"
    CONCEPTS = "concepts"
    PROBLEM_SOLVING = "problem_solving"

"""
- Maps each `PromptType` to some prompt text or template from `prompts.py`.
"""
PROMPT_TEMPLATES = {
    PromptType.REWRITE_TEXT: prompts.REWRITE_PROMPT,
    PromptType.CONCEPTS: prompts.CONCEPT_FLASHCARD_PROMPT,
    PromptType.PROBLEM_SOLVING: prompts.PROBLEM_FLASHCARD_PROMPT,
}


def create_system_message(prompt_type: PromptType, **kwargs) -> str:
    template = PROMPT_TEMPLATES.get(prompt_type, "")
    return template.format(**kwargs)


def call_llm(
    system_message: str,
    user_content,
    response_format,
    content_type: str,
    run_as_image: bool = False,
):
    global convo_hist
    messages = []

    gpt_4o = "gpt-4o-2024-08-06"
    gpt_4o_mini = "gpt-4o-mini"

    model = gpt_4o if run_as_image else gpt_4o_mini


    # Append the user message
    if run_as_image:
        # For images, we pass a structured "image_url" message
        messages.append({"role": "system", "content": system_message})
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{user_content}"}
                    }
                ],
            }
        )
    else:
        # Normal text content
        if not convo_hist:
            convo_hist.append({"role": "system", "content": system_message})

        convo_hist.append({"role": "user", "content": user_content})
    # Log the final user-facing messages we send to the LLM (except raw base64 to avoid console clutter)
    if run_as_image:
        console.log(f"[bold cyan]Messages sent to `{model}`:[/bold cyan]", "Image (excluded base64 for brevity)")
    else:
        console.log(f"[bold cyan]Messages sent to `{model}`:[/bold cyan]", "Convo_hist" if not messages else messages)
    # Send the request to the LLM
    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages if run_as_image else convo_hist,
            response_format=response_format,
            max_completion_tokens=16384,
            temperature=0,
            top_p=0.1,
        )
    except Exception as e:
        logger.error("Error calling LLM for content_type='%s': %s", content_type, e, exc_info=True)
        raise
    # Extract final text response
    response = completion.choices[0].message.content

    convo_hist.append({"role": "assistant", "content": response})

    if not run_as_image:
        print_log("Conversation history BEFORE pruning", model, completion.usage)

    if len(convo_hist) > 4:
        del convo_hist[1:3]

    if not run_as_image:
        print_log("Conversation history AFTER pruning", model, completion.usage)

    # Log assistant response
    console.log(f"[bold yellow]`{model}` response:[/bold yellow]\n")
    if response_format == "text":
        format_utils.print_message("assistant", response, None, None, markdown=True)
    else:
        format_utils.print_message("assistant", response, response_format, None, markdown=False)
    # Log token usage
    usage_info = completion.usage
    console.log("[bold green]Token Usage:[/bold green]", usage_info)

    return response


def print_log(
        name: str,
        model: str,
        token_usage: dict
) -> None:
    console.rule(f"[bold red]{name}[/bold red]")
    console.log("\n[bold cyan]System message:[/bold cyan]\n", convo_hist[0]['content'])
    console.log("\n[bold cyan]User message:[/bold cyan]\n", convo_hist[-2]['content'])
    console.log(f"\n[bold yellow]{model} response:[/bold yellow]\n", convo_hist[-1]['content'])
    console.log("\n[bold red]Token usage:[/bold red]\n", token_usage)