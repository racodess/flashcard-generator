"""
Handles the extraction of textual content from standard (non-image/PDF) websites.
Utilizes `trafilatura` to fetch and convert HTML to Markdown.
After obtaining the Markdown, it breaks the content into sections by headings
to enable fine-grained flashcard generation.

Usage scenario:
    1. Provide a URL to `process_url(...)`.
    2. The function fetches the HTML from the URL.
    3. The HTML is extracted/converted into Markdown.
    4. The Markdown is sliced into sections by headings (H1-H6).
    5. If an `ignore_list` is supplied, sections with titles matching any ignored heading are skipped.
    6. A dictionary containing the URL and a list of sections (title + content) is returned.
"""
import re

from rich.console import Console
from trafilatura import fetch_url, extract
from trafilatura.settings import use_config

from utils.flashcard_logger import logger

console = Console()


def process_url(
        url: str,
        ignore_list=None
) -> dict:
    """
    Fetches and extracts textual content from the given URL, converting it into Markdown.
    The Markdown is then subdivided by headings.

    Steps:
      - Fetch the URL via `trafilatura.fetch_url(url)`.
      - Extract Markdown using `trafilatura.extract(..., output_format="markdown")`.
      - Break the Markdown into sections by headings (handled in `_get_headers`).
      - Optionally remove sections whose headings match entries in `ignore_list`.

    Args:
        url (str): The webpage URL to fetch and parse.
        ignore_list (list, optional): A list of heading titles to exclude (case-insensitive).

    Returns:
        dict: A structure containing:
          {
            "url": <the URL string>,
            "sections": [
              {
                "title": <heading text>,
                "content": <markdown content up to the next heading>
              },
              ...
            ]
          }

        If no content is extracted or all headings are filtered out, returns an empty dict.
    """
    logger.info("Fetching content from: %s", url)
    downloaded_html = fetch_url(url)
    if not downloaded_html:
        logger.error("Failed to download content from %s", url)
        return {}

    # Prepare Trafilatura config (e.g., you could adjust minimum text length or other parameters)
    config = use_config()
    extracted_markdown = extract(
        downloaded_html,
        config=config,
        output_format="markdown",
        include_comments=False,
        include_tables=False,
        with_metadata=False
    )
    if not extracted_markdown:
        # If no textual content could be extracted, log a warning and return an empty dict
        logger.warning("No textual content extracted from %s", url)
        return {}

    # Parse the extracted markdown into structured heading-based sections
    sections = _get_headers(extracted_markdown)

    # Optionally remove sections based on the ignore_list
    if ignore_list:
        sections = _skip_headers(sections, ignore_list)

    # If no valid sections remain, log a warning and return an empty dict
    if not sections:
        logger.warning("No headings were found or all headings filtered out from %s", url)
        return {}

    # Return the URL and the processed sections
    return {
        "url": url,
        "sections": sections
    }


def _get_headers(markdown_text: str) -> list:
    """
    Splits the provided Markdown text into sections based on Markdown headings (#, ##, ###, etc.).

    Implementation details:
      - Uses a regular expression to identify lines that begin with 1-6 '#' characters
        followed by a space and some text.
      - Each identified heading marks the start of a new section.
      - Accumulates lines following a heading until the next heading is encountered.

    Args:
        markdown_text (str): A string containing the entire Markdown text.

    Returns:
        list: A list of dictionaries in the form:
            [
                {
                    "title": <the heading text (without '#' characters)>,
                    "content": <all lines under this heading until the next heading>,
                },
                ...
            ]
    """
    # This regex looks for lines beginning with one or more '#' up to 6, then some whitespace, then the heading text
    heading_regex = re.compile(
        r'^(#{1,6})\s+(.*)$',
        re.MULTILINE
    )
    lines = markdown_text.splitlines()
    sections = []
    current_title = None
    current_content = []

    # Iterate over each line in the Markdown text
    for line in lines:
        match = heading_regex.match(line)
        if match:
            # When a new heading is found, store the previous heading section (if any)
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title.strip(),
                        "content": "\n".join(current_content).strip()
                    }
                )
            # Reset current_title and current_content for this new heading
            current_title = match.group(2)
            current_content = []
        else:
            # Accumulate lines that are not headings into the current section
            current_content.append(line)

    # After iterating, if there's a final heading section, add it to the list
    if current_title is not None:
        sections.append(
            {
                "title": current_title.strip(),
                "content": "\n".join(current_content).strip()
            }
        )
    return sections


def _skip_headers(
        sections: list,
        ignore_list: list
) -> list:
    """
    Removes sections whose headings match any title in `ignore_list`.

    Matching is done in a case-insensitive manner.

    Args:
        sections (list): List of dictionaries where each dictionary represents a section:
                         {"title": <heading>, "content": <section content>}.
        ignore_list (list): List of headings to ignore.

    Returns:
        list: A filtered list of sections, excluding those whose `title` appears in `ignore_list`.
    """
    # Convert ignore_list entries to lowercase for case-insensitive comparison
    lowered_ignores = {s.lower() for s in ignore_list}
    filtered = []
    for section in sections:
        heading_text = section["title"].lower()
        # If the heading text is not in the ignore list, keep it
        if heading_text not in lowered_ignores:
            filtered.append(section)
        # Otherwise, skip the entire section
    return filtered
