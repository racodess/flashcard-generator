import os
from rich.console import Console

from utils import models, format_utils, file_utils, importer, templates
from utils.llm_utils import (
    PromptType,
    get_flashcards, get_rewrite, get_system_message, get_tags
)
from utils.flashcard_logger import logger
from utils.scraper import process_url

console = Console()

conversation = []


def generate_flashcards(
    file_path=None,
    url=None,
    metadata=None,
    flashcard_type='general',
    anki_media_path=None,
):
    # Determine content_type and source identifiers
    content_type = "url" if url else "text"
    url_name = url if url else ""
    source_name = os.path.basename(file_path) if file_path else ""

    if url:
        # Fetch and parse URL
        webpage_data = process_url(url, metadata['ignore_sections'])
        if not webpage_data:
            logger.warning("No data returned from URL: %s. Skipping flashcard generation.", url)
            return
        # Process the chunked content
        chunks = webpage_data.get("sections", [])
        _process_chunks(
            chunks=chunks,
            card_type=flashcard_type,
            tags=metadata['anki_tags'],
            url_name=url_name,
            file_name=source_name,
            content_type=content_type
        )
        return
    elif file_path:
        detected_type = file_utils.get_content_type(file_path, url=None)
        if detected_type == 'unsupported':
            logger.warning("Unsupported file type: %s. Skipping flashcard generation.", file_path)
            return
        content_type = detected_type.lower()
        try:
            file_content = file_utils.get_data(file_path, content_type)
        except file_utils.UnsupportedFileTypeError as e:
            logger.warning("Unsupported file type error: %s", e)
            return
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return

        chunk = [
            {"title": source_name, "content": file_content}
        ]
        _process_chunks(
            chunks=chunk,
            card_type=flashcard_type,
            tags=metadata['anki_tags'],
            url_name=url_name,
            file_name=source_name,
            content_type=content_type,
            media_path=anki_media_path
        )
        return
    else:
        logger.error("Neither file_path nor url provided to generate_flashcards.")
        return


def _run_generic_flow(
    *,
    flow_name: str,
    prompt_type: PromptType,
    content: str,
    tags: list,
    url_name: str,
    file_name: str,
    content_type: str,
    model_class,        # e.g. models.ProblemFlashcard or models.Flashcard
    template_name: str,     # e.g. "AnkiConnect: Problem" or "AnkiConnect: Basic"
    media_path: str = None, # only used in concept flow for PDF creation
):
    console.rule(f"Running {flow_name}")

    # Rewrite the content without storing in conversation history
    if content_type in ["text", "url"]:
        rewritten_text = get_rewrite(
            user_message=content,
            content_type=content_type
        )

        # Optionally create PDF if it's plain text
        if content_type == "text" and media_path:
            format_utils.make_pdf(
                media_path=media_path,
                file_name=file_name,
                text=rewritten_text
            )
    else:
        # For images/PDFs
        rewritten_text = content

    # Create or update the flashcard conversation with the prompt for flashcards
    system_message = get_system_message(prompt_type, tags=tags)

    response = get_flashcards(
        conversation=conversation,
        system_message=system_message,
        user_text=rewritten_text,
        run_as_image=(content_type not in ["text", "url"]),  # e.g., PDF, image, etc.
        response_format=model_class
    )

    if tags:
        response = get_tags(
            user_message=response,
            tags=tags,
            model_class=model_class
        )

    # Validate model and fill metadata
    card_model = model_class.model_validate_json(response)

    format_utils.set_data_fields(
        card_model=card_model,
        url_name=url_name,
        file_name=file_name,
        content_type=content_type
    )

    # Print flashcards for debugging
    format_utils.print_flashcards(card_model.flashcards)
    importer.anki_import(card_model, template_name=template_name)

    return card_model


def _run_problem_flow(
        content,
        tags,
        url_name,
        source_name,
        content_type
):
    return _run_generic_flow(
        flow_name="Problem-solving Flow",
        prompt_type=PromptType.PROBLEM_SOLVING,
        content=content,
        tags=tags,
        url_name=url_name,
        file_name=source_name,
        content_type=content_type,
        model_class=models.ProblemFlashcard,
        template_name=templates.PROBLEM_CARD_NAME,
    )


def _run_concept_flow(
        content,
        tags,
        url_name,
        file_name,
        content_type,
        media_path
):
    return _run_generic_flow(
        flow_name="Concepts Flow",
        prompt_type=PromptType.CONCEPTS,
        content=content,
        tags=tags,
        url_name=url_name,
        file_name=file_name,
        content_type=content_type,
        model_class=models.Flashcard,
        template_name=templates.BASIC_CARD_NAME,
        media_path=media_path
    )


def _process_chunks(
        chunks,
        card_type,
        tags,
        url_name,
        file_name,
        content_type,
        media_path=None
):
    console.rule(
        f"[bold red]Extracted and Filtered Webpage Data[/bold red]"
    )
    if content_type in ["text", "url"]:
        console.log(f"[bold red]Chunks:[/bold red]", chunks)
    else:
        console.log(f"[bold red]Chunks:[/bold red]", "Image placeholder text.")
    for idx, chunk in enumerate(
            chunks,
            start=1
    ):
        heading_title = chunk.get(
            "title",
            file_name
        )
        chunk_text = chunk["content"]

        logger.info(f"Generating flashcards from chunk {idx}: {heading_title}")
        console.rule(f"[bold red]Chunk {idx}:[/bold red] {heading_title}")

        # Show chunk in console for debugging if it's text
        if content_type == "text" or content_type == "url":
            console.print(chunk_text)
        else:
            console.print("Image placeholder text")

        if card_type == 'problem':
            _run_problem_flow(
                content=chunk_text,
                tags=tags,
                url_name=url_name,
                source_name=file_name,
                content_type=content_type
            )
        else:
            _run_concept_flow(
                content=chunk_text,
                tags=tags,
                url_name=url_name,
                file_name=file_name,
                content_type=content_type,
                media_path=media_path
            )
