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


def run_problem_flow(content, tags, url_name, source_name, content_type):
    """
    Encapsulates the repeated steps for 'problem-solving flow' prompts.
    Returns the validated `ProblemFlashcard` model.
    """
    console.rule("Running PROBLEM_FLASHCARD Prompt from Problem-solving Flow")

    system_message = create_system_message(PromptType.PROBLEM_FLASHCARD, tags=tags)
    response = call_llm(
        system_message=system_message,
        user_content=content,
        response_format=models.ProblemFlashcard,
        content_type=content_type,
        # For files like PDFs or images, we pass `True`, but for a chunked URL text or .txt file we pass `False`.
        run_as_image=(content_type not in ["text", "url"])
    )

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
    Returns the validated `Flashcard` model (the final concept-based flashcard set).
    """
    console.rule("Running CONCEPT_MAP Prompt from Concepts Flow")

    # 1) Generate a concept map
    system_message = create_system_message(PromptType.CONCEPT_MAP)
    concept_map_response = call_llm(
        system_message=system_message,
        user_content=content,
        response_format=prompts.TEXT_FORMAT,
        content_type=content_type,
        run_as_image=(content_type not in ["text", "url"])
    )

    # 2) Optionally create a PDF from the concept map if we have a local .txt file
    if content_type == "text":
        format_utils.create_pdf_from_markdown(anki_media_path, source_name, concept_map_response)

    console.rule("Running CONCEPT_LIST Prompt from Concepts Flow")

    # 3) Extract concepts list
    system_message = create_system_message(PromptType.CONCEPT_LIST, tags=tags)
    concepts_list_response = call_llm(
        system_message=system_message,
        user_content=concept_map_response,
        response_format=models.Concepts,
        content_type=content_type
    )
    concepts_list = format_utils.parse_concepts_list_response(concepts_list_response)

    console.rule("Running DRAFT_FLASHCARD Prompt from Concepts Flow")

    # 4) Draft flashcards
    system_message = create_system_message(PromptType.DRAFT_FLASHCARD)
    draft_flashcard_response = call_llm(
        system_message=system_message,
        user_content=f"#### The list of each concept item to be addressed:\n{concepts_list}",
        response_format=models.Flashcard,
        content_type=content_type
    )

    console.rule("Running FINAL_FLASHCARD Prompt from Concepts Flow")

    # 5) Final flashcards with optimized wording
    system_message = create_system_message(PromptType.FINAL_FLASHCARD)
    final_flashcard_response = call_llm(
        system_message=system_message,
        user_content=f"#### The first draft of flashcards:\n{draft_flashcard_response}",
        response_format=models.Flashcard,
        content_type=content_type
    )

    concept_flashcard_model = models.Flashcard.model_validate_json(final_flashcard_response)
    fill_data_fields(concept_flashcard_model, url_name=url_name, source_name=source_name, content_type=content_type)

    # Display and import
    format_utils.print_message("flashcard", concept_flashcard_model.flashcards, None, None, markdown=False)
    importer.add_flashcards_to_anki(concept_flashcard_model, template_name="AnkiConnect: Basic")

    return concept_flashcard_model


def process_chunked_content(chunks, flashcard_type, tags, url_name, source_name, content_type, anki_media_path):
    """
    Helper to iterate through chunks (like web sections) or a single chunk (like file content),
    and run either problem-solving or concept-based flows.
    """
    for idx, chunk in enumerate(chunks, start=1):
        heading_title = chunk.get("title", source_name)  # fallback for file-based chunk
        chunk_text = chunk["content"]

        logger.info(f"Generating flashcards from chunk {idx}: {heading_title}")

        # Show chunk in console for clarity or debugging unless it's a base64 encoded str
        console.rule(f"Chunk {idx}: {heading_title}")

        if content_type == "text" or content_type == "json":
            console.print(chunk_text)
        else:
            console.print("Image")
        print("\n" * 3)

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
    tags=None,
    flashcard_type='general',
    anki_media_path=None,
):
    """
    Entry point for generating flashcards:

    Inputs:
        - Either a `file_path` or a `url`,
        - A list of `tags`,
        - A `flashcard_type` (`general` or `problem`),
        - The Anki media path.

    Steps:
        1. Get content:
            - If `url` is provided, calls `scraper.fetch_and_parse_url(url)`, then extracts text from headings and elements,
            - Else if `file_path` is given, calls `file_utils` to read the file.
            - Logs warnings if unsupported file types or empty content.

        2. Branch by `flashcard_type`:
            - `problem`:
                * Use the problem-solving flow prompts
            - `general` (concept-based):
                * Use the concept-based flow prompts.
    """
    if tags is None:
        tags = []

    # Determine content_type and source identifiers
    content_type = "url" if url else "text"
    url_name = url if url else ""
    source_name = os.path.basename(file_path) if file_path else ""

    if url:
        # 1) Fetch and parse URL
        webpage_data = fetch_and_parse_url(url)
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
        process_chunked_content(chunks, flashcard_type, tags, url_name, source_name, content_type, anki_media_path)
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
        process_chunked_content(single_chunk, flashcard_type, tags, url_name, source_name, content_type, anki_media_path)
        return

    else:
        logger.error("Neither file_path nor url provided to generate_flashcards.")
        return
