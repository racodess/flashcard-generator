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

from utils import models, prompts, format_utils, file_utils, importer
from utils.llm_utils import (
    PromptType,
    create_system_message,
    call_llm
)
from utils.flashcard_logger import logger
from utils.scraper import fetch_and_parse_url, chunk_webpage

console = Console()


def fill_data_fields(flashcard_obj, url_name, source_name, content_type):
    """
    - Adds extra metadata fields to each flashcard as required by the Anki add-on "pdf viewer and editor".
    """
    for fc in flashcard_obj.flashcards:
        fc.data.image = source_name if content_type == "image" else ""
        fc.data.external_source = source_name if content_type != "image" else ""
        fc.data.external_page = 1
        fc.data.url = url_name


def rewrite_content(content, content_type):
    system_message = create_system_message(PromptType.REWRITE_TEXT)
    rewritten_chunk = run_llm_call(system_message, content, models.TEXT_FORMAT, content_type)

    # Log rewritten chunk for debugging
    console.log("[bold red] Rewritten chunk:\n", rewritten_chunk)

    return rewritten_chunk


def run_llm_call(system_message, content, response_format, content_type):
    return call_llm(
        system_message=system_message,
        user_content=content,
        response_format=response_format,
        content_type=content_type,
        # For files like PDFs or images, we pass `True`, but for a chunked URL text or .txt file we pass `False`.
        run_as_image=(content_type not in ["text", "url"])
    )


def run_problem_flow(content, tags, url_name, source_name, content_type):
    """
    Encapsulates the repeated steps for 'problem-solving flow' prompts.
    Returns the validated `ProblemFlashcard` model.
    """
    console.rule("Running PROBLEM_FLASHCARD Prompt from Problem-solving Flow")

    system_message = create_system_message(PromptType.PROBLEM_SOLVING, tags=tags)
    response = run_llm_call(system_message, content, models.ProblemFlashcard, content_type)

    # Parse and fill metadata
    problem_flashcard_model = models.ProblemFlashcard.model_validate_json(response)
    fill_data_fields(problem_flashcard_model, url_name=url_name, source_name=source_name, content_type=content_type)

    # Display and import
    format_utils.print_message("problem_flashcards", problem_flashcard_model, None, None, markdown=False)
    importer.add_flashcards_to_anki(problem_flashcard_model, template_name="AnkiConnect: Problem")

    return problem_flashcard_model


def run_concept_flow(content, tags, url_name, source_name, content_type, anki_media_path):
    """
    Encapsulates the repeated steps for 'concept-based flow' prompts.
    Returns the validated `Flashcard` model (the concept-based flashcard set).
    """
    console.rule("Running FLASHCARD Prompt from Concepts Flow")

    # Rewrite plain text or url chunks to improve clarity and formatting for the LLM input
    if content_type == 'text' or content_type == 'url':
        content = rewrite_content(content, content_type)
        # Optionally create high-quality pdf from plain text for reference within flashcards
        format_utils.create_pdf_from_markdown(anki_media_path, source_name, content) if content_type == 'text' else None

    system_message = create_system_message(PromptType.CONCEPTS, tags=tags)
    concept_response = run_llm_call(system_message, content, models.Flashcard, content_type)

    concept_flashcard_model = models.Flashcard.model_validate_json(concept_response)
    fill_data_fields(concept_flashcard_model, url_name=url_name, source_name=source_name, content_type=content_type)

    # Display and import
    format_utils.print_message("flashcard", concept_flashcard_model.flashcards, None, None, markdown=False)
    importer.add_flashcards_to_anki(concept_flashcard_model, template_name="AnkiConnect: Basic")

    return concept_flashcard_model


def process_chunked_content(chunks, flashcard_type, tags, url_name, source_name, content_type, anki_media_path=None):
    """
    Helper to iterate through chunks (like web sections) or a single chunk (like file content),
    and run either problem-solving or concept-based flows.
    """
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
        # 1) Fetch and parse URL
        webpage_data = fetch_and_parse_url(url, metadata['ignore_headings'])
        if not webpage_data:
            logger.warning("No data returned from URL: %s. Skipping flashcard generation.", url)
            return

        # 2) Chunk the webpage
        sections = webpage_data.get("sections", [])
        chunks = chunk_webpage(sections)
        if not chunks:
            logger.warning("No chunked headings found for URL: %s", url)
            return

        # 3) Process the chunked content with either problem-flow or concept-flow
        process_chunked_content(chunks, flashcard_type, metadata['local_tags'], url_name, source_name, content_type)
        return

    elif file_path:
        # 1) Identify content type
        detected_type = file_utils.get_content_type(file_path, url=None)
        if detected_type == 'unsupported':
            logger.warning("Unsupported file type: %s. Skipping flashcard generation.", file_path)
            return
        content_type = detected_type.lower()

        # 2) Read the file
        try:
            file_content = file_utils.process_data(file_path, content_type)
        except file_utils.UnsupportedFileTypeError as e:
            logger.warning("Unsupported file type error: %s", e)
            return
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return

        # 3) For simplicity, treat the entire file as a single "chunk"
        single_chunk = [{"title": source_name, "content": file_content}]

        # 4) Process with either problem-flow or concept-flow
        process_chunked_content(single_chunk, flashcard_type, metadata['local_tags'], url_name, source_name, content_type, anki_media_path)
        return

    else:
        logger.error("Neither file_path nor url provided to generate_flashcards.")
        return