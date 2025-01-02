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

import utils
import models
import prompts
import importer
import file_utils
import format_utils
from llm_utils import (
    PromptType,
    create_system_message,
    call_llm
)
from flashcard_logger import logger
from scraper import fetch_and_parse_url, extract_text_from_item

console = Console()


def fill_data_fields(flashcard_obj, source_name, content_type):
    """
    - Adds extra metadata fields (image name or external source name) to each flashcard as required by the Anki add-on "pdf viewer and editor".
    """
    for fc in flashcard_obj.flashcards:
        if content_type == "image":
            fc.data.image = source_name
            fc.data.external_source = ""
        else:
            fc.data.image = ""
            fc.data.external_source = source_name
        fc.data.external_page = 1


# TODO: Implement knowledge graph
def generate_flashcards(
    file_path=None,
    url=None,
    tags=None,
    flashcard_type='general',
    anki_media_path=None,
    used_dir=None,
    relative_path=""
):
    """
    Single entry point for generating flashcards:

    - Inputs:
        - Either a `file_path` or a `url`,
        - A list of `tags`,
        - A `flashcard_type` (`general` or `problem`),
        - The Anki media path.

    - Steps:
        1. Get content:
            - If `url` is provided, calls `scraper.fetch_and_parse_url(url)`, then extracts text from headings and elements,
            - Else if `file_path` is given, calls `file_utils` to read the file.
            - Logs warnings if unsupported file types or empty content.

        2. Get source name:
            - Sets it to the URL or the file’s basename (the final part of the path).

        3. Branch by `flashcard_type`:
            - `problem`:
                1. Creates a “system message” for problem flashcards,
                2. Calls the LLM to produce the “problem-flashcard” model (structured steps, approaches, solutions, etc.),
                3. Print them and import them to Anki.

            - `general` (concept-based):
                1. Generate a concept map (`PromptType.CONCEPT_MAP`) from the content,
                2. Create a PDF from that concept map if the input was a plain text .txt file with no URLs (for reference in Anki),
                3. Extract a concept list from the concept map (`PromptType.CONCEPT_LIST`),
                4. Draft flashcards (`PromptType.DRAFT_FLASHCARD`),
                5. Generate finalized flashcards from the draft set with optimized wording (`PromptType.FINAL_FLASHCARD`),
                6. Print them and import them to Anki.
    """
    if tags is None:
        tags = []

    content_type = "url" if url else "text"
    file_content = ""

    # Step 1: Retrieve data from URL or local file
    if url:
        # Fetch and parse URL content
        # Intended for URLs containing text content, not remote resources (e.g. img, pdf)
        webpage_data = fetch_and_parse_url(url)
        if not webpage_data:
            logger.warning("No data returned from URL: %s. Skipping flashcard generation.", url)
            return

        sections = webpage_data.get("sections", [])
        lines = []
        for item in sections:
            extracted_text = extract_text_from_item(item)
            if extracted_text:
                lines.append(extracted_text)
        file_content = "\n\n".join(lines)

        if not file_content.strip():
            logger.warning("No textual content found for URL: %s", url)
            return

    elif file_path:
        # Identify content type from file, read data
        detected_type = file_utils.get_content_type(file_path, url=None)
        if detected_type == 'unsupported':
            logger.warning("Unsupported file type: %s. Skipping flashcard generation.", file_path)
            return

        content_type = detected_type.lower()
        try:
            file_content = file_utils.process_data(file_path, content_type)
        except file_utils.UnsupportedFileTypeError as e:
            logger.warning("Unsupported file type error: %s", e)
            return
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return
    else:
        logger.error("Neither file_path nor url provided to generate_flashcards.")
        return

    # Identify the source name
    source_name = url if url else os.path.basename(file_path)

    # Step 2: If 'problem' -> Problem-solving flow
    if flashcard_type == 'problem':
        # ----- Problem-solving-based flow -----

        # Build system message for problem flashcards
        system_message = create_system_message(PromptType.PROBLEM_FLASHCARD, tags=tags)

        """
        - Make LLM call (use_image_model=True for "image" analysis, if needed),
        - Currently, all non-txt files (PDFs, and images) are handled as images for simplicity.
        """
        response = call_llm(
            system_message=system_message,
            user_content=file_content,
            response_format=models.ProblemFlashcard,
            content_type=content_type,
            run_as_image=True
        )

        # Parse into custom Pydantic model defined in `models.py`
        problem_flashcard_model = models.ProblemFlashcard.model_validate_json(response)
        fill_data_fields(problem_flashcard_model, source_name, content_type)

        # Print & import to Anki
        utils.print_message("problem_flashcards", problem_flashcard_model, None, None, markdown=False)
        importer.add_flashcards_to_anki(problem_flashcard_model, template_name="AnkiConnect: Problem")

    else:
        # ----- Concept-based flow -----

        # 1) Generate a concept map from the source material
        system_message = create_system_message(PromptType.CONCEPT_MAP)
        concept_map_response = call_llm(
            system_message=system_message,
            user_content=file_content,
            response_format=prompts.TEXT_FORMAT,
            content_type=content_type,
            run_as_image=(content_type not in ["text", "url"])
        )

        # 2) Optionally convert concept map to PDF (for non-URL plain text-based content in `.txt` files)
        if content_type in ["text"]:
            format_utils.create_pdf_from_markdown(anki_media_path, source_name, concept_map_response)

        # 3) Extract list of concept items from the concept map
        system_message = create_system_message(PromptType.CONCEPT_LIST, tags=tags)
        concepts_list_response = call_llm(
            system_message=system_message,
            user_content=concept_map_response,
            response_format=models.Concepts,
            content_type=content_type
        )
        concepts_list = utils.parse_concepts_list_response(concepts_list_response)

        # 4) Draft set of flashcards
        system_message = create_system_message(PromptType.DRAFT_FLASHCARD)
        draft_flashcard_response = call_llm(
            system_message=system_message,
            user_content=f"#### The list of each concept item to be addressed:\n{concepts_list}",
            response_format=models.Flashcard,
            content_type=content_type
        )

        # 5) Final set of flashcards with optimized wording
        system_message = create_system_message(PromptType.FINAL_FLASHCARD)
        final_flashcard_response = call_llm(
            system_message=system_message,
            user_content=f"#### The first draft of flashcards:\n{draft_flashcard_response}",
            response_format=models.Flashcard,
            content_type=content_type
        )

        concept_flashcard_model = models.Flashcard.model_validate_json(final_flashcard_response)
        fill_data_fields(concept_flashcard_model, source_name, content_type)

        # Display finalized flashcards to terminal
        utils.print_message("flashcard", concept_flashcard_model.flashcards, None, None, markdown=False)

        # Import finalized flashcards to Anki
        importer.add_flashcards_to_anki(concept_flashcard_model, template_name="AnkiConnect: Basic")