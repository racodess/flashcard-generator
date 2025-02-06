"""
Orchestrates the creation of flashcards using a Large Language Model (LLM) pipeline.

High-Level Overview:
    - Accepts both local file paths and URLs to generate flashcards from.
    - Identifies content type (text, PDF, image, etc.) and retrieves or parses the content.
    - Optionally rewrites text for clarity using an LLM before flashcard creation.
    - Breaks content into sections (chunks) and routes them through specialized flows:
        * "Problem-solving" flow for more involved, step-by-step question/answer cards.
        * "Concepts" flow for simpler Q&A flashcards.
    - Validates, tags, and imports the resulting flashcards into Anki using AnkiConnect.

Typical Usage:
    1. Call `generate_flashcards(file_path=...)` or `generate_flashcards(url=...)`.
    2. The script determines the content type and retrieves text accordingly.
    3. Text is optionally rewritten for clarity, then chunked by headings or sections.
    4. Each chunk is passed to either the "problem" or "general/concept" flow.
    5. The finished flashcards, along with any specified tags, are imported into Anki.

Key Components:
    - `generate_flashcards(...)`: Entry point that orchestrates parsing, rewriting (if needed),
      and flashcard creation from a local file or URL.
    - `_process_chunks(...)`: Iterates over chunked content, dispatching to the appropriate flow.
    - `_run_problem_flow(...)` / `_run_concept_flow(...)`: Specialized methods for generating
      flashcards suited to problem-solving or conceptual Q&A.
    - `_run_generic_flow(...)`: Internal helper that handles LLM prompting, response parsing,
      tagging, and final validation before importing to Anki.

This script is typically called by higher-level logic (e.g., from `host.py`) whenever new files
or URLs are discovered that require flashcard generation. It relies on modules for LLM interaction,
file handling, and Anki integration to provide an end-to-end solution.
"""
import os
from rich.console import Console
from utils import (
    models,
    format_utils,
    file_utils,
    llm_utils,
    importer,
    templates,
    flashcard_logger,
    scraper
)

console = Console()

# Maintains a global conversation list if needed by certain prompt flows.
conversation = []


def generate_flashcards(
    file_path=None,
    url=None,
    metadata=None,
    flashcard_type='general',
    anki_media_path=None,
    pdf_viewer_path=None,
):
    """
    Orchestrates the entire process of creating flashcards, either from a local file or a URL.

    Steps (when given a URL):
      1. Fetch webpage data (HTML) using `process_url(url, ignore_sections)`.
      2. Convert HTML to Markdown, chunk the content by headings.
      3. Pass the chunked sections to `_process_chunks(...)` to generate flashcards.

    Steps (when given a local file):
      1. Check file type (e.g., PDF, image, text).
      2. Read the file content using `file_utils.get_data(...)`.
      3. Create a single chunk (title + content) and pass it to `_process_chunks(...)`.

    Args:
        file_path (str, optional): Path to the local file. Defaults to None.
        url (str, optional): A URL for fetching data. Defaults to None.
        metadata (dict, optional): Extra metadata including:
            - "anki_tags": list of tags to add to flashcards.
            - "ignore_sections": list of headings to ignore for chunking.
        flashcard_type (str, optional): Determines if it's a 'problem' flow or 'general/concept' flow.
        anki_media_path (str, optional): Path to the Anki media directory, relevant for PDF creation, backup, and syncing.
        pdf_viewer_path (str): Path to the Anki add-on 'pdf viewer and editor' required directory, relevant for PDF creation, and allowing the Anki add-on to access the file on any OS.

    Behavior:
        - If both file_path and url are None, logs an error and exits.
        - If the file type is unsupported, logs a warning and exits.
        - If content was successfully retrieved and chunked, calls `_process_chunks(...)`.
    """
    # Decide if the content is from a URL or a local file
    content_type = "url" if url else "text"
    url_name = url if url else ""
    source_name = os.path.basename(file_path) if file_path else ""

    if url:
        # When a URL is provided, process with the scraper to retrieve textual data
        webpage_data = scraper.process_url(url, metadata['ignore_sections'])
        if not webpage_data:
            # No data extracted from the URL, so we skip flashcard generation
            flashcard_logger.logger.warning("No data returned from URL: %s. Skipping flashcard generation.", url)
            return
        chunks = webpage_data.get("sections", [])
        # Pass the extracted sections (chunks) for flashcard generation
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
        # Identify the file's content type (image, pdf, text, etc.)
        detected_type = file_utils.get_content_type(
            file_path=file_path,
            url=None
        )
        if detected_type == 'unsupported':
            flashcard_logger.logger.warning("Unsupported file type: %s. Skipping flashcard generation.", file_path)
            return
        content_type = detected_type.lower()

        # Attempt to read the file content
        try:
            file_content = file_utils.get_data(file_path, content_type)
        except file_utils.UnsupportedFileTypeError as e:
            flashcard_logger.logger.warning("Unsupported file type error: %s", e)
            return
        except Exception as e:
            # Catch other possible errors (permissions, I/O errors, etc.)
            flashcard_logger.logger.error("Error reading file %s: %s", file_path, e)
            return

        # Wrap the content in a single chunk, using the filename as title
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
            anki_media_path=anki_media_path,
            pdf_viewer_path=pdf_viewer_path
        )
        return
    else:
        # Neither a URL nor a file was specified
        flashcard_logger.logger.error("Neither file_path nor url provided to generate_flashcards.")
        return


def _run_generic_flow(
    *,
    flow_name: str,
    prompt_type: llm_utils.PromptType,
    content: str,
    tags: list,
    url_name: str,
    file_name: str,
    content_type: str,
    model_class,           # e.g., models.ProblemFlashcard or models.Flashcard
    template_name: str,    # e.g., templates.PROBLEM_CARD_NAME or templates.BASIC_CARD_NAME
    anki_media_path: str = None, # Used for storing generated PDFs (from plain text) for backup and syncing with Anki
    pdf_viewer_path: str = None # Used for making generated PDFs (from plain text) accessible within Anki flashcard reviews
):
    """
    A helper method that encapsulates the standard steps to generate flashcards
    for either 'problem-solving' or 'conceptual' content.

    The flow includes:
      - (Optionally) rewriting text-based content to ensure it's well-structured.
      - Generating flashcards via an LLM call (`get_flashcards(...)`).
      - Validating the final result against the corresponding pydantic model class.
      - Setting extra fields (e.g., source file, URL name).
      - Printing debug info and importing to Anki.

    Args:
        flow_name (str): A descriptive name used for console logs (e.g., "Problem-solving Flow").
        prompt_type (PromptType): Specifies which system message template to use.
        content (str): The text or minimal data for the LLM to process.
        tags (list): Any additional tags to append to generated flashcards.
        url_name (str): A reference to the original source URL (if any).
        file_name (str): The local file name for the content (if any).
        content_type (str): The type of content ("text", "pdf", "image", "url", etc.).
        model_class (pydantic BaseModel): The model class that represents the structure
            of the flashcards generated (e.g., ProblemFlashcard).
        template_name (str): The Anki note type or template name to use during import.
        anki_media_path (str, optional): The path to Anki's media folder if needed for PDF generation.
        pdf_viewer_path (str): The path to the Anki add-on 'pdf viewer and editor' required directory, if needed for PDF generation.

    Returns:
        A model_class instance containing validated flashcard data, or None if something went wrong.
    """
    print()
    console.rule(f"Running {flow_name}")

    # If the content is textual (URL or plain text), we attempt a rewrite to improve clarity
    if content_type in ["text", "url"]:
        rewritten_text = llm_utils.get_rewrite(
            user_message=content,
            content_type=content_type
        )

        # If a media_path is provided and content is text, we optionally turn it into a PDF
        if content_type == "text" and anki_media_path:
            format_utils.make_pdf(
                anki_media_path=anki_media_path,
                pdf_viewer_path=pdf_viewer_path,
                file_name=file_name,
                text=rewritten_text
            )
    else:
        # For images, PDFs, etc., we skip rewriting and use the raw content
        rewritten_text = content

    # Prepare the system message for the LLM based on the prompt_type and tags
    system_message = llm_utils.get_system_message(prompt_type, tags=tags)

    # Generate flashcards using the LLM. If the content is not text/url, specify run_as_image=True
    response = llm_utils.get_flashcards(
        conversation=conversation,
        system_message=system_message,
        user_text=rewritten_text,
        run_as_image=(content_type not in ["text", "url"]),  # For image/PDF flows
        response_format=model_class
    )

    # Convert JSON response to a validated pydantic model instance
    card_model = model_class.model_validate_json(response)

    # Insert extra info (URL, filename, content type) into the model
    format_utils.set_data_fields(
        card_model=card_model,
        url_name=url_name,
        file_name=file_name,
        content_type=content_type
    )

    # Display the generated flashcards in the console (debugging)
    format_utils.print_flashcards(card_model.flashcards)
    # Push the flashcards into Anki via importer
    importer.anki_import(
        flashcards_model=card_model,
        template_name=template_name
    )
    return card_model


def _run_problem_flow(
        content,
        tags,
        url_name,
        source_name,
        content_type
):
    """
    Initiates the specialized "Problem-solving" flow for flashcard generation,
    leveraging the `_run_generic_flow` with `PromptType.PROBLEM_SOLVING`.

    Args:
        content (str): The chunk of text to generate flashcards from.
        tags (list): Any additional tags for the flashcards.
        url_name (str): The original source URL if available.
        source_name (str): The local file name or fallback heading.
        content_type (str): The content type (e.g., text, url, pdf, image).

    Returns:
        A ProblemFlashcard model instance (with one or more flashcards).
    """
    return _run_generic_flow(
        flow_name="Problem-solving Flow",
        prompt_type=llm_utils.PromptType.PROBLEM_SOLVING,
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
        anki_media_path,
        pdf_viewer_path
):
    """
    Initiates the more general "Concepts" flow for flashcard generation
    (e.g., basic Q&A cards), leveraging the `_run_generic_flow`
    with `PromptType.CONCEPTS`.

    Args:
        content (str): The chunk of text from which flashcards will be generated.
        tags (list): Any additional tags to add to the flashcards.
        url_name (str): The original URL if available.
        file_name (str): The local file name if processing a file.
        content_type (str): Indicates whether it's text, PDF, URL, image, etc.
        anki_media_path (str): Path to Anki's media folder for optional PDF creation; stores backup and allows syncing of Anki files.
        pdf_viewer_path (str): Path to Anki's media folder for optional PDF creation; makes file accessible during Anki flashcard reviews.

    Returns:
        A Flashcard model instance (with one or more flashcards).
    """
    return _run_generic_flow(
        flow_name="Concepts Flow",
        prompt_type=llm_utils.PromptType.CONCEPTS,
        content=content,
        tags=tags,
        url_name=url_name,
        file_name=file_name,
        content_type=content_type,
        model_class=models.Flashcard,
        template_name=templates.BASIC_CARD_NAME,
        anki_media_path=anki_media_path,
        pdf_viewer_path=pdf_viewer_path
    )


def _merge_chunks(
        chunks,
        file_name
):
    """
    Merges chunks based on a minimum token length. Larger chunks are kept as-is. This method is not intended for images.

    - Chunks < min_chunk_tokens tokens are merged until the total would exceed max_chunk_tokens tokens, at which point we flush the accumulated "buffer" and start a new one.

    - Chunks >= min_chunk_tokens tokens are treated as standalone chunks (we flush any buffer first, then place that chunk by itself).

    This ensures no chunk is lost: every piece of text is either merged
    or included in the final set of merged chunks for flashcard generation.

    Args:
        chunks (list): A list of dictionaries, each representing a section:
                       [
                         {
                           "title": <section title>,
                           "content": <section content>
                         },
                         ...
                       ]
        file_name (str): Source file name, used for reference.

    Returns:
        A list of merged chunks.
    """
    merged_chunks = []

    # Temporary buffer for accumulating small chunks
    content_buffer = []
    running_token_count = 0

    def flush_temp_buffer():
        """
        Push the current buffer into merged_chunks if it's not empty.
        """
        nonlocal content_buffer, running_token_count

        merged_chunks.append(
            {"title": "Merged chunks", "content": ""}
        )
        for chunk in content_buffer:
            merged_chunks[-1]['content'] += f"{chunk['title']}:\n{chunk['content']}\n------\n"

        # Reset the buffer
        content_buffer = []
        running_token_count = 0

    min_chunk_tokens = 300
    max_chunk_tokens = 1000

    for idx, chunk in enumerate(chunks, start=1):
        heading_title = chunk.get("title", file_name)
        chunk_text = chunk["content"]

        chunk_tokens = llm_utils.get_num_tokens(chunk_text)

        flashcard_logger.logger.info(
            f"[Chunk] '{heading_title}' has {chunk_tokens} tokens."
        )

        # Decide how to handle the chunk based on token count:
        if chunk_tokens < min_chunk_tokens:
            # This chunk is small; try to fit it into the buffer
            if running_token_count + chunk_tokens <= max_chunk_tokens:
                # It fits in the buffer without exceeding max_chunk_tokens
                flashcard_logger.logger.info(
                    f"Merging chunk ('{heading_title}') "
                    f"into buffer (current total={running_token_count} tokens)."
                )
                content_buffer.append(
                    {"title": heading_title, "content": chunk_text}
                )
                running_token_count += chunk_tokens
            else:
                # Adding this chunk would exceed max_chunk_tokens tokens: flush the buffer first
                flashcard_logger.logger.info(
                    f"Buffer ~{running_token_count} tokens; flushing before adding chunk "
                    f"{idx} ('{heading_title}')."
                )
                flush_temp_buffer()

                # Start a fresh buffer with the current chunk
                content_buffer.append(
                    {"title": heading_title, "content": chunk_text}
                )
                running_token_count = chunk_tokens
        else:
            # This chunk is >= min_chunk_tokens tokens
            # Flush the current buffer first (if it's not empty)
            if running_token_count > 0:
                flashcard_logger.logger.info(
                    f"Flushing buffer (~{running_token_count} tokens) before adding "
                    f"larger chunk {idx} ('{heading_title}')."
                )
                flush_temp_buffer()

            # Treat it as a single chunk
            flashcard_logger.logger.info(
                f"Processing chunk ('{heading_title}') as a standalone chunk."
            )
            merged_chunks.append(
                {"title": heading_title, "content": chunk_text}
            )

    # Flush any leftover data in the buffer
    if running_token_count > 0:
        flashcard_logger.logger.info(
            f"Flushing final buffer (~{running_token_count} tokens)."
        )
        flush_temp_buffer()

    return merged_chunks


def _process_chunks(
        chunks,
        card_type,
        tags,
        url_name,
        file_name,
        content_type,
        anki_media_path=None,
        pdf_viewer_path=None
):
    """
    Iterates over chunked content (sections of text or placeholders),
    generating flashcards for each chunk.

    For each chunk:
      - Logs the heading/title in the console.
      - If it's text-based, prints the actual text to the console for debug.
      - If it's a 'problem' card_type, runs `_run_problem_flow(...)`.
      - Otherwise, runs `_run_concept_flow(...)`.

    Args:
        chunks (list): A list of dictionaries, each representing a section:
                       [
                         {
                           "title": <section title>,
                           "content": <section content>
                         },
                         ...
                       ]
        card_type (str): Type of flashcard flow ('problem' or 'general').
        tags (list): Additional tags to add.
        url_name (str): Source URL if available.
        file_name (str): Source file name, used for reference.
        content_type (str): Format of the data (e.g., "text", "url", "pdf", "image").
        anki_media_path (str, optional): Path to Anki media directory (for PDF creation if text).
        pdf_viewer_path (str): Path to the Anki add-on 'pdf viewer and editor' required directory (for PDF creation if text).
    """
    print()
    console.rule("[bold red]Extracted and Filtered Data[/bold red]")

    if content_type in ["text", "url"]:
        chunks = _merge_chunks(
            chunks=chunks,
            file_name=file_name
        )

    for idx, chunk in enumerate(chunks, start=1):
        heading_title = chunk.get("title", file_name)
        chunk_text = chunk["content"]

        print()
        console.rule(f"[bold red]Chunk {idx}:[/bold red] {heading_title}")

        if content_type in ["text", "url"]:
            console.print(chunk_text)

            # Extract first 3 lines for tag generation
            sample_lines = '\n'.join(chunk_text.split('\n')[:7])

            # Get filtered tags from LLM
            filtered_tags = llm_utils.get_tags(
                user_message=sample_lines,
                tags=tags,
                model_class=models.TEXT_FORMAT
            )
        else:
            console.print("Image placeholder text")
            filtered_tags = tags

        console.log("[bold red] Filtered tags:[/bold red]", filtered_tags)

        # Decide which flow to run based on the card_type
        if card_type == 'problem':
            _run_problem_flow(
                content=chunk_text,
                tags=filtered_tags,
                url_name=url_name,
                source_name=file_name,
                content_type=content_type
            )
        else:
            _run_concept_flow(
                content=chunk_text,
                tags=filtered_tags,
                url_name=url_name,
                file_name=file_name,
                content_type=content_type,
                anki_media_path=anki_media_path,
                pdf_viewer_path=pdf_viewer_path
            )
