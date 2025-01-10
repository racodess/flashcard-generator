"""
Purpose:

- Deals with textual websites (not images/PDFs).
- Uses the `trafilatura` to fetch and extract textual HTML, plus `BeautifulSoup` to parse headings.
"""
from rich.console import Console
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
from trafilatura.settings import Extractor

from utils.flashcard_logger import logger

console = Console()


def fetch_and_parse_url(url: str, ignore_list=None) -> dict:
    """
    - Calls `trafilatura.fetch_url(url)`, then `extract(...)` with some custom `Extractor(...)` settings,
    - Returns a JSON/dict with the URL and a list of “sections,” each of which is a structured representation of headings (H1, H2, etc.) and textual content.
    """
    logger.info("Fetching content from: %s", url)
    downloaded_html = fetch_url(url)
    if not downloaded_html:
        logger.error("Failed to download content from %s", url)
        return None

    options = Extractor(output_format="html", with_metadata=True)
    extracted_html = extract(downloaded_html, options=options)
    if not extracted_html:
        logger.warning("No textual content extracted from %s", url)
        return None

    soup = BeautifulSoup(extracted_html, "html.parser")
    parsed_sections = parse_headings_to_tree(soup)

    # Log parsed sections before filter for debugging
    console.log("[bold red] Parsed sections before filtering:",  parsed_sections)

    # Optionally skip headings under `ignore_heading` in metadata.yaml
    if ignore_list:
        parsed_sections = skip_headings(parsed_sections, ignore_list)

        # Log parsed sections before filter for debugging
        console.log("[bold red] Filtered sections:",  parsed_sections)

    # Build the final webpage data
    webpage_data = {
        "url": url,
        "sections": parsed_sections
    }
    return webpage_data


def parse_headings_to_tree(soup) -> list:
    """
    - Recursively walks the `<body>` to find headings (`<h1>...</h6>`) and paragraphs/other elements, building a hierarchical structure
    - If an element is not inside a heading, it is added at the top level as an "uncategorized element"

    ```
    {
    "type": "heading",
    "tag": "h2",
    "content": "Some heading text",
    "children": [... nested elements or headings ...]
    }
    ```

    Returns:
        list: A list of section objects (headings) and/or element objects
    """
    sections = []
    heading_stack = {level: None for level in range(1, 7)}

    def create_section_object(tag, text):
        return {
            "type": "heading",
            "tag": tag,
            "content": text,
            "children": []
        }

    def create_element_object(tag, text, attrs=None):
        return {
            "type": "element",
            "tag": tag,
            "content": text,
            "attrs": attrs or {}
        }

    container = soup.body if soup.body else soup

    for elem in container.descendants:
        # Skip non-element (NavigableString, comments, etc.)
        if elem.name is None:
            continue

        tag_name = elem.name.lower()
        # Build hierarchy for headers h1 to h6
        if tag_name in [f"h{i}" for i in range(1, 7)]:
            level = int(tag_name[1])  # e.g. "h2" -> level=2
            heading_text = elem.get_text(strip=True)
            if not heading_text:
                continue

            section_obj = create_section_object(tag_name, heading_text)
            if level == 1:
                sections.append(section_obj)
                heading_stack[1] = section_obj

                # Reset deeper heading references
                for deeper in range(2, 7):
                    heading_stack[deeper] = None
            else:
                # If we have an h2/h3/etc. but no h1 yet, create a pseudo-h1 to hold it.
                if heading_stack[1] is None:
                    pseudo_h1 = create_section_object("h1", "Untitled Section")
                    sections.append(pseudo_h1)
                    heading_stack[1] = pseudo_h1

                parent_level = level - 1
                while parent_level > 0 and not heading_stack.get(parent_level):
                    parent_level -= 1
                parent_section = heading_stack.get(parent_level)
                if parent_section:
                    parent_section["children"].append(section_obj)

                heading_stack[level] = section_obj

                # Reset deeper heading references
                for deeper in range(level + 1, 7):
                    heading_stack[deeper] = None
        # For non-header elements
        else:
            content_text = elem.get_text(strip=True)
            if not content_text:
                continue

            attrs = dict(elem.attrs) if elem.attrs else {}
            element_obj = create_element_object(tag_name, content_text, attrs)
            attached = False

            # Attach this element to the closest heading in the stack
            for lvl in range(6, 0, -1):
                if heading_stack[lvl] is not None:
                    heading_stack[lvl]["children"].append(element_obj)
                    attached = True
                    break

            # If there's no heading, place it at root level
            if not attached:
                uncategorized_element = create_section_object(elem.name, "Uncategorized Element")
                sections.append(uncategorized_element)

    return sections


def skip_headings(sections: list, ignore_list: list) -> list:
    """
    Recursively removes any heading whose content matches one of the ignored headings
    (case-insensitive). All child nodes of that heading are also removed.
    """
    filtered_sections = []
    lowered_ignores = {s.lower() for s in ignore_list}  # For case-insensitive matching

    for section in sections:
        if section.get("type") == "heading":
            heading_text = section.get("content", "").strip().lower()
            if heading_text in lowered_ignores:
                # Skip this heading & all its children
                continue
            # Otherwise, recursively filter the heading's children
            children = section.get("children", [])
            section["children"] = skip_headings(children, ignore_list)
            filtered_sections.append(section)
        else:
            # If it's an 'element' or something else, keep it
            filtered_sections.append(section)

    return filtered_sections


def chunk_webpage(sections: list) -> list[dict]:
    """
    Recursively chunks the 'sections' list (usually top-level headings from parse_headings_to_tree)
    so that:
      - If there are multiple headings at the current level, chunk by each heading.
      - If there's only one heading at the current level, skip that level and chunk deeper.

    Returns a list of dicts like:
        [
          {
            "title": "Heading Title",
            "content": "All textual content under this heading"
          },
          ...
        ]
    """
    # Base case: no sections
    if not sections:
        return []

    # If there are multiple headings at this level, chunk by each heading
    if len(sections) > 1:
        chunks = []
        for heading_node in sections:
            if heading_node.get("type") == "heading":
                chunk_title = heading_node.get("content", "Untitled Heading")
                # Gather all text from this heading_node (including its subheadings/children)
                chunk_content = extract_text_from_item(heading_node)
                chunks.append({
                    "title": chunk_title,
                    "content": chunk_content
                })
            else:
                # It's possible we have top-level 'element' or something else
                pass
        return chunks

    # If there's exactly one heading at this level, skip chunking at this level:
    # go deeper into its children, looking for multiple subheadings there.
    single_heading = sections[0]
    if single_heading.get("type") != "heading":
        # If it's not a heading (could be an 'element'), just skip
        return []

    # The single heading might have a bunch of children (which may themselves be headings or elements)
    # We'll extract just the child headings:
    child_headings = [
        child for child in single_heading.get("children", [])
        if child.get("type") == "heading"
    ]

    # If the heading has multiple child headings, chunk by each child heading
    if len(child_headings) > 1:
        chunks = []
        for child in child_headings:
            chunk_title = child.get("content", "Untitled Subheading")
            chunk_content = extract_text_from_item(child)
            chunks.append({
                "title": chunk_title,
                "content": chunk_content
            })
        return chunks

    # If there's exactly one child heading, we skip that level again (go deeper)
    if len(child_headings) == 1:
        return chunk_webpage(child_headings)
    else:
        # If the single heading has no child headings at all, then we treat that heading as a chunk
        chunk_title = single_heading.get("content", "Untitled Heading")
        chunk_content = extract_text_from_item(single_heading)
        return [{
            "title": chunk_title,
            "content": chunk_content
        }]


def extract_text_from_item(item: dict) -> str:
    """
    - Recursively accumulates all textual content from headings & sub-elements, returning a single large text string.
    - This is used by `openai_generator.py` to feed textual content into the LLM.
    """
    if item.get("type") == "element":
        # Return the element content as plain text
        return item.get("content", "").strip()
    elif item.get("type") == "heading":
        heading_title = item.get("content", "Untitled Section")
        child_text = []

        for child in item.get("children", []):
            child_text.append(extract_text_from_item(child))

        return f"## {heading_title}\n\n" + "\n\n".join(child_text)

    return ""
