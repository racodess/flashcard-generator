"""
Purpose:

- Deals with textual websites (not images/PDFs).
- Uses `trafilatura` to fetch and extract textual HTML as Markdown. Then we chunk the markdown
  by headings to create sections suitable for flashcard generation.
"""
import re

from rich.console import Console
from trafilatura import fetch_url, extract
from trafilatura.settings import use_config

from utils.flashcard_logger import logger

console = Console()


def fetch_and_parse_url(url: str, ignore_list=None) -> dict:
    """
    - Calls `trafilatura.fetch_url(url)`,
    - Extracts content as Markdown using `extract(..., output_format="md")`,
    - Parses the Markdown into sections (one section per heading),
    - Optionally skips headings listed in `ignore_list`.

    Returns:
        {
            "url": <the URL string>,
            "sections": [
                {
                  "title": <heading text>,
                  "content": <all lines until the next heading>
                },
                ...
            ]
        }
    """
    logger.info("Fetching content from: %s", url)
    downloaded_html = fetch_url(url)
    if not downloaded_html:
        logger.error("Failed to download content from %s", url)
        return {}

    # Prepare Trafilatura config
    # Example: limiting the minimum text length or including images/links if you prefer
    # config.set("DEFAULT", "MIN_LENGTH", "120")
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
        logger.warning("No textual content extracted from %s", url)
        return {}

    # Now parse the extracted markdown into heading-based sections
    sections = parse_markdown_headings(extracted_markdown)

    # Optionally skip headings using ignore_list
    if ignore_list:
        sections = skip_markdown_headings(sections, ignore_list)

    if not sections:
        logger.warning("No headings were found or all headings filtered out from %s", url)
        return {}

    return {
        "url": url,
        "sections": sections
    }


def parse_markdown_headings(markdown_text: str) -> list:
    """
    Splits the markdown into sections by top-level markdown headings (`#`, `##`, etc.).

    Returns:
        A list of dicts:
        [
            {
                "title": <the heading string>,
                "content": <the lines belonging to that heading>,
            },
            ...
        ]
    """
    # Regex to capture lines that start with '#' (1-6).
    heading_regex = re.compile(r'^(#{1,6})\s+(.*)$', re.MULTILINE)

    lines = markdown_text.splitlines()
    sections = []
    current_title = None
    current_content = []

    for line in lines:
        match = heading_regex.match(line)
        if match:
            # We have encountered a new heading
            if current_title is not None:
                # Store the previous heading section
                sections.append({
                    "title": current_title.strip(),
                    "content": "\n".join(current_content).strip()
                })
            # Reset for this new heading
            current_title = match.group(2)
            current_content = []
        else:
            # Not a heading, accumulate text in the current section
            current_content.append(line)

    # Handle the last heading in the file
    if current_title is not None:
        sections.append({
            "title": current_title.strip(),
            "content": "\n".join(current_content).strip()
        })

    return sections


def skip_markdown_headings(sections: list, ignore_list: list) -> list:
    """
    Filters out entire sections whose `title` matches a heading in `ignore_list`
    (case-insensitive). Each section is a dict with "title" and "content".
    """
    lowered_ignores = {s.lower() for s in ignore_list}
    filtered = []
    for section in sections:
        heading_text = section["title"].lower()
        if heading_text in lowered_ignores:
            # Skip the entire section
            continue
        filtered.append(section)
    return filtered
