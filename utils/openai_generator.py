"""
Purpose: heart of the logic that reads data -> generates flashcards with LLM calls -> sends to Anki.

- This is the main code that decides how to **create flashcards** from content:
  1. Collect raw data (from file or URL),
  2. Depending on `flashcard_type`, either do a “problem-solving flow” or a “concept-based flow”,
  3. Interact with the LLM in multiple steps for more consistent higher-quality outputs (like generating concept maps, extracting concept lists, drafting flashcards, finalizing flashcard drafts),
  4. Finally, programmatically import the flashcards to Anki using `importer.py`.

**Important Note:**

- Requires Anki add-on "AnkiConnect":
    - A third-party API that exposes HTTP endpoints of Anki functionality (e.g. creating decks, adding notes).

- "AnkiConnect" Add-on requires Anki to be open on the user's system,
    - Otherwise, this application results in an error at the import step.
"""
import os

from rich.console import Console

from utils import models, format_utils, file_utils, importer, templates
from utils.llm_utils import (
    PromptType,
    create_system_message,
    call_llm
)
from utils.flashcard_logger import logger
from utils.scraper import fetch_and_parse_url

console = Console()


def rewrite_content(content, content_type):
    system_message = create_system_message(PromptType.REWRITE_TEXT)
    rewritten_chunk = call_llm(
        system_message=system_message,
        user_content=content,
        response_format=models.TEXT_FORMAT,
        content_type=content_type,
        # For files like PDFs or images, we pass `True`, but for a chunked URL text or .txt file we pass `False`.
        run_as_image=(content_type not in ["text", "url"])
    )

    # Log rewritten chunk for debugging
    console.log("[bold red] Rewritten chunk:\n", rewritten_chunk)

    return rewritten_chunk


def run_generic_flow(
    *,
    flow_name: str,
    prompt_type: PromptType,
    content: str,
    tags: list,
    url_name: str,
    source_name: str,
    content_type: str,
    response_model_class,        # e.g. models.ProblemFlashcard or models.Flashcard
    anki_template_name: str,     # e.g. "AnkiConnect: Problem" or "AnkiConnect: Basic"
    message_print_name: str,     # e.g. "problem_solving_flashcards" or "concept_flashcards"
    anki_media_path: str = None, # only used in concept flow for PDF creation
):
    """
    A generic flow runner that consolidates common steps:
        1. Optional rewriting of content (for text/url).
        2. Creating system message.
        3. Calling the LLM and validating the JSON.
        4. Filling metadata.
        5. Printing and importing to Anki.
    """
    console.rule(f"Running {flow_name}")

    # Flow-specific rewriting, e.g. for concept flow with plain text or webpage chunks
    if content_type in ["text", "url"]:
        content = rewrite_content(content, content_type)
        # Optionally create PDF if it's plain text for referencing source material within flashcards
        if content_type == "text" and anki_media_path:
            format_utils.create_pdf_from_markdown(anki_media_path, source_name, content)

    system_message = create_system_message(prompt_type, tags=tags)

    # Files like PDFs or images → run_as_image = True, else False
    run_as_image = content_type not in ["text", "url"]

    # Call the LLM
    response = call_llm(
        system_message=system_message,
        user_content=content,
        response_format=response_model_class,
        content_type=content_type,
        run_as_image=run_as_image
    )

    # Validate and fill metadata
    validated_model = response_model_class.model_validate_json(response)
    format_utils.fill_data_fields(validated_model, url_name=url_name, source_name=source_name, content_type=content_type)

    # Print flashcards for debugging
    format_utils.print_message(message_print_name, validated_model.flashcards, None, None, markdown=False)

    # Import to Anki
    importer.add_flashcards_to_anki(validated_model, template_name=anki_template_name)

    return validated_model


def run_problem_flow(content, tags, url_name, source_name, content_type):
    """
    Encapsulates the repeated steps for 'problem-solving flow' prompts.
    Returns the validated `ProblemFlashcard` model.
    """
    return run_generic_flow(
        flow_name="Problem-solving Flow",
        prompt_type=PromptType.PROBLEM_SOLVING,
        content=content,
        tags=tags,
        url_name=url_name,
        source_name=source_name,
        content_type=content_type,
        response_model_class=models.ProblemFlashcard,
        anki_template_name=templates.PROBLEM_CARD_NAME,
        message_print_name="problem_solving_flashcards"
    )


def run_concept_flow(content, tags, url_name, source_name, content_type, anki_media_path):
    """
    Encapsulates the repeated steps for 'concept-based flow' prompts.
    Returns the validated `Flashcard` model (the concept-based flashcard set).
    """
    return run_generic_flow(
        flow_name="Concepts Flow",
        prompt_type=PromptType.CONCEPTS,
        content=content,
        tags=tags,
        url_name=url_name,
        source_name=source_name,
        content_type=content_type,
        response_model_class=models.Flashcard,
        anki_template_name=templates.BASIC_CARD_NAME,
        message_print_name="concept_flashcards",
        # Provide a rewriting function and media path for PDF generation
        anki_media_path=anki_media_path
    )


def process_chunked_content(chunks, flashcard_type, tags, url_name, source_name, content_type, anki_media_path=None):
    """
    Helper to iterate through chunks (like web sections) or a single chunk (like file content),
    and run either problem-solving or concept-based flows.
    """

    console.rule(f"[bold red]Extracted and Filtered Webpage Data[/bold red]")
    console.log(f"[bold red]Chunks:[/bold red]", chunks)

    for idx, chunk in enumerate(chunks, start=1):
        heading_title = chunk.get("title", source_name)  # fallback for file-based chunk
        chunk_text = chunk["content"]

        logger.info(f"Generating flashcards from chunk {idx}: {heading_title}")
        # Show chunk in console for clarity or debugging unless it's a base64 encoded str
        console.rule(f"[bold red]Chunk {idx}:[/bold red] {heading_title}")

        if content_type == "text" or content_type == "json":
            console.print(chunk_text)
        else:
            console.print("Image")

        if flashcard_type == 'problem':
            run_problem_flow(
                content=chunk_text,
                tags=tags,
                url_name=url_name,
                source_name=source_name,
                content_type=content_type
            )
        else:
            run_concept_flow(
                content=chunk_text,
                tags=tags,
                url_name=url_name,
                source_name=source_name,
                content_type=content_type,
                anki_media_path=anki_media_path
            )


def generate_flashcards(
    file_path=None,
    url=None,
    metadata=None,
    flashcard_type='general',
    anki_media_path=None,
):
    """
    Entry point for generating flashcards:

    Inputs:
        - Either a `file_path` or a `url`,
        - A metadata dict,
        - A `flashcard_type` (`general` or `problem`),
        - The Anki media path.

    Steps:
        1. Get content:
            - If `url` is provided, calls `scraper.fetch_and_parse_url(url)`, then extracts text from headings and elements,
            - Else if `file_path` is given, calls `file_utils` to read the file.
            - Logs warnings if unsupported file types or empty content.
    """
    # Determine content_type and source identifiers
    content_type = "url" if url else "text"
    url_name = url if url else ""
    source_name = os.path.basename(file_path) if file_path else ""

    if url:
        # Fetch and parse URL
        webpage_data = fetch_and_parse_url(url, metadata['ignore_sections'])
        if not webpage_data:
            logger.warning("No data returned from URL: %s. Skipping flashcard generation.", url)
            return
        # Process the chunked content with either problem-flow or concept-flow
        chunks = webpage_data.get("sections", [])
        process_chunked_content(chunks, flashcard_type, metadata['anki_tags'], url_name, source_name, content_type)
        return
    elif file_path:
        # Identify content type
        detected_type = file_utils.get_content_type(file_path, url=None)
        if detected_type == 'unsupported':
            logger.warning("Unsupported file type: %s. Skipping flashcard generation.", file_path)
            return
        content_type = detected_type.lower()
        # Read the file
        try:
            file_content = file_utils.process_data(file_path, content_type)
        except file_utils.UnsupportedFileTypeError as e:
            logger.warning("Unsupported file type error: %s", e)
            return
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return
        # Process with either problem-flow or concept-flow
        # For simplicity, treat the entire file as a single "chunk"
        chunk = [{"title": source_name, "content": file_content}]
        process_chunked_content(chunk, flashcard_type, metadata['anki_tags'], url_name, source_name, content_type, anki_media_path)
        return
    else:
        logger.error("Neither file_path nor url provided to generate_flashcards.")
        return