"""
LLM utility functions to interface with a custom LLM client (`OpenAI` in this code).

This module provides:
    - Enumeration `PromptType` for differentiating LLM prompt categories.
    - Methods (`get_rewrite`, `get_tags`, `get_flashcards`) that format, send, and process LLM requests.
    - Internal method `_get_completion` for actually calling the LLM endpoint.
    - A global `conversation` used to maintain context across multiple calls (useful for chat-style interactions).
"""
from enum import Enum

from rich.console import Console
from openai import OpenAI

from utils import prompts, models
from utils.flashcard_logger import logger

console = Console()
client = OpenAI()


class PromptType(Enum):
    """
    Represents different types of LLM prompts used within the system.
    Each enum value maps to a distinct prompt template in `PROMPT_TEMPLATES`.

    - CONCEPTS: Generating concept-based flashcards (e.g., Q&A).
    - PROBLEM_SOLVING: Generating problem-solving flashcards (e.g., steps, approach).
    - TAGS: Appending or manipulating tags for generated content.
    - REWRITE_TEXT: Rewriting or summarizing text to a more refined version.
    """
    CONCEPTS = "concepts"
    PROBLEM_SOLVING = "problem_solving"
    TAGS = "tags"
    REWRITE_TEXT = "rewrite_text"


# Maps each PromptType to a specific string template from `utils.prompts`.
PROMPT_TEMPLATES = {
    PromptType.CONCEPTS: prompts.CONCEPT_FLASHCARD_PROMPT,
    PromptType.PROBLEM_SOLVING: prompts.PROBLEM_FLASHCARD_PROMPT,
    PromptType.TAGS: prompts.TAG_PROMPT,
    PromptType.REWRITE_TEXT: prompts.REWRITE_PROMPT
}


def get_system_message(
        prompt_type: PromptType,
        **kwargs
) -> str:
    """
    Retrieves the appropriate prompt template for the provided `prompt_type`,
    then formats it by injecting any `kwargs` into the template via `str.format()`.

    Args:
        prompt_type (PromptType): The type of prompt (CONCEPTS, PROBLEM_SOLVING, etc.).
        **kwargs: Additional placeholders for template formatting.

    Returns:
        str: The formatted system message (prompt) that will be sent to the LLM.
    """
    template = PROMPT_TEMPLATES.get(prompt_type, "")
    return template.format(**kwargs)


def get_rewrite(user_message, content_type):
    """
    Rewrites or refines a block of text via the LLM.

    Steps:
      1. Fetches the rewrite prompt template (REWRITE_TEXT).
      2. Constructs a system message and a user message.
      3. Calls `_get_completion(...)` to obtain the rewritten text.

    Args:
        user_message (str): The text to be rewritten.
        content_type (str): Helps determine if we treat the content as text or another medium.

    Returns:
        str: The LLM’s rewritten version of the provided text.
    """
    system_message = get_system_message(
        prompt_type=PromptType.REWRITE_TEXT
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    completion = _get_completion(
        messages=messages,
        response_format=models.TEXT_FORMAT,
        run_as_image=(content_type not in ["text", "url"])
    )
    return completion.choices[0].message.content


def get_tags(
        user_message,
        tags,
        model_class
):
    """
    Adds or processes tags for flashcards or other LLM-generated content.

    Steps:
      1. Retrieves the tag prompt template (TAGS).
      2. Substitutes the user-provided list of tags into the template.
      3. Sends the system message (with tags) and user message to the LLM.
      4. Returns the result with updated tags embedded.

    Args:
        user_message (str): The existing text or flashcard representation.
        tags (list): A list of tags to integrate.
        model_class (pydantic model): The expected LLM response format.

    Returns:
        str: The LLM’s response (usually JSON-encoded) incorporating the tags.
    """
    system_message = get_system_message(
        prompt_type=PromptType.TAGS,
        tags=tags
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    completion = _get_completion(
        messages=messages,
        response_format=model_class,
    )
    return completion.choices[0].message.content


def get_flashcards(
        conversation,
        system_message,
        user_text,
        run_as_image,
        response_format
):
    """
    Generates flashcards using the LLM, optionally passing an image placeholder if `run_as_image` is True.

    Steps:
      1. If no prior conversation, prepend the system message to start context.
      2. Depending on `run_as_image`, either send a text user message or an "image_url" placeholder.
      3. Call `_get_completion(...)` to get the LLM’s response.
      4. Append the response to the `conversation`.
      5. Print the entire conversation for debugging.
      6. Truncate older messages if conversation grows too long (keeps context somewhat fresh).
      7. Return the response text.

    Args:
        conversation (list): A running list of messages (dicts) for conversation context.
        system_message (str): The formatted prompt to guide the LLM for this set of flashcards.
        user_text (str): The actual text (or path) to generate flashcards from.
        run_as_image (bool): True if the user_text is an image or PDF, requiring different input handling.
        response_format (pydantic model): The data structure for the LLM’s result.

    Returns:
        str: The LLM-generated content (flashcards or instructions) as a string.
    """
    if not conversation:
        conversation.append({"role": "system", "content": system_message})

    messages = []
    if run_as_image:
        # Provide an image placeholder in the user content to handle non-text inputs
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
        # Otherwise, treat it as normal text
        conversation.append({"role": "user", "content": user_text})

    completion = _get_completion(
        messages=messages if run_as_image else conversation,
        response_format=response_format,
        run_as_image=run_as_image
    )
    response = completion.choices[0].message.content

    # Maintain the conversation by appending the LLM’s response
    conversation.append({"role": "assistant", "content": response})

    # Print out the conversation in the console for debugging
    for item in conversation:
        for k, v in item.items():
            if k == "role":
                console.log(f"\n[bold red]{k}:[/bold red]", v)
            else:
                console.log(f"[bold red]{k}:[/bold red]\n", v)

    # If the conversation is getting too large, prune some middle messages
    if len(conversation) > 4:
        del conversation[1:3]

    console.log("\n[bold red]Token Usage:[/bold red]", completion.usage)

    return response


def _get_completion(
    messages: list,
    response_format,
    run_as_image: bool = False
):
    """
    Internal method to make the actual LLM API call via `client.beta.chat.completions.parse`.

    It chooses one of two models based on whether we are sending image data or plain text:
      - `gpt-4o-2024-08-06` if `run_as_image` is True.
      - `gpt-4o-mini` otherwise.

    Args:
        messages (list): The conversation or prompt messages to send.
        response_format (pydantic model or TEXT_FORMAT): The expected format of the return data.
        run_as_image (bool, optional): If True, the model expects image-based input. Defaults to False.

    Returns:
        openai.ChatCompletion: An object containing choices and usage info for the LLM’s response.

    Raises:
        Exception: If the LLM call fails or times out.
    """
    gpt_4o = "gpt-4o-2024-08-06"
    gpt_4o_mini = "gpt-4o-mini"
    model = gpt_4o if run_as_image else gpt_4o_mini

    if run_as_image:
        console.log("[bold cyan]Image placeholder text.[/bold cyan]")
    else:
        console.log("[bold cyan]Message sent to LLM:[/bold cyan]", messages)

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

    console.log(f"[bold yellow]`{model}` response:[/bold yellow]", completion.choices[0].message.content)
    return completion
