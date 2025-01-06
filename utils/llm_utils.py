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

- GPT-o1:
    - Not currently used,
    - Chain-of-thought model,
    - High cost,
    - Highest-quality output.
    
- GPT-o1-mini:
    - Not currently used,
    - Chain-of-thought model,
    - Moderate cost, but pricier than GPT-4o,
    - Higher-quality output.
    
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
GPT_O1 = "o1-2024-12-17"
GPT_O1_MINI = "o1-mini-2024-09-12"
GPT_4O = "gpt-4o-2024-08-06"
GPT_4O_MINI = "gpt-4o-mini"

console = Console()
client = OpenAI()


class PromptType(Enum):
    """
    - The different types of LLM prompts,
    - Defined in `prompts.py`.
    """
    CONCEPT_MAP = "concept_map"
    CONCEPT_LIST = "concept_list"
    DRAFT_FLASHCARD = "draft_flashcard"
    FINAL_FLASHCARD = "final_flashcard"
    PROBLEM_FLASHCARD = "problem_flashcard"

"""
- Maps each `PromptType` to some prompt text or template from `prompts.py`.
"""
PROMPT_TEMPLATES = {
    PromptType.CONCEPT_MAP: prompts.CONCEPT_MAP_PROMPT,
    PromptType.CONCEPT_LIST: prompts.CONCEPTS_LIST_PROMPT,
    PromptType.DRAFT_FLASHCARD: prompts.DRAFT_FLASHCARD_PROMPT,
    PromptType.FINAL_FLASHCARD: prompts.FINAL_FLASHCARD_PROMPT,
    PromptType.PROBLEM_FLASHCARD: prompts.PROBLEM_FLASHCARD_PROMPT,
}


def create_system_message(prompt_type: PromptType, **kwargs) -> str:
    """
    - Formats the relevant prompt template (in `PROMPT_TEMPLATES`) with additional context (e.g. local tags, previous responses), returning the final “system message” for the LLM.
    """
    template = PROMPT_TEMPLATES.get(prompt_type, "")
    return template.format(**kwargs)


def call_llm(
    system_message: str,
    user_content,
    response_format,
    content_type: str,
    run_as_image: bool = False,
):
    """
    Builds the message list with:

    - A “system” message (from `create_system_message`)
    - A “user” message, which can be either raw text or base64 encoded image if `run_as_image=True`
    - Sends the request to the LLM using OpenAI's `client.beta.chat.completions.parse` API for structured output using Pydantic models defined in `models.py`
    - Extracts the best text result from the LLM, logs usage, returns the string
    """
    # Decide model based on whether we need "image analysis" or not
    model = GPT_4O if run_as_image else GPT_4O_MINI

    # Build message list
    messages = [{"role": "system", "content": system_message}]

    if run_as_image:
        # Treat user content as an "image request" structure required by OpenAI API
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{user_content}"
                        }
                    }
                ]
            }
        )
    else:
        # Normal text content
        messages.append({"role": "user", "content": user_content})

    # Log message history sent as input to OpenAI API
    console.log(f"[bold cyan]Messages sent to `{model}`:[/bold cyan]", messages)

    try:
        completion = client.beta.chat.completions.parse( # For structured output using pydantic models
            model=model, # OpenAI LLM
            messages=messages, # Conversation history
            response_format=response_format, # For text or structured output
            max_completion_tokens=16384, # Input+output can use quite a lot of tokens; ensures we stay within "max output token" limit of GPT-4o & GPT-4o-mini, but o1 models go much higher.
            temperature=0, # For deterministic output
            top_p=0.1, # For deterministic output; chooses within the top 10% most likely tokens
        )
    except Exception as e:
        logger.error("Error calling LLM for content_type='%s': %s", content_type, e, exc_info=True)
        raise

    if not completion.choices:
        logger.warning("No completion choices returned for content_type='%s'.", content_type)
        return ""

    finish_reason = completion.choices[0].finish_reason
    if finish_reason != "stop":
        logger.warning(
            "LLM finished processing content_type='%s' with reason: %s",
            content_type, finish_reason
        )

    # Extract final text response
    response = completion.choices[0].message.content

    # Log assistant response based on message history
    if response_format == "text":
        console.log(f"[bold yellow]`{model}` response:[/bold yellow]\n")
        format_utils.print_message("assistant", response, None, None, markdown=True)
    else:
        console.log(f"[bold yellow]`{model}` response:[/bold yellow]\n")
        format_utils.print_message("assistant", response, response_format, None, markdown=False)

    # Log token usage info
    usage_info = completion.usage
    console.log("[bold green]Token Usage:[/bold green]", usage_info)

    return response