TEXT_FORMAT = {"type": "text"}


PLACEHOLDER_MESSAGE = "See below for assistant's analysis of the image:"


REWRITE_PROMPT = """
Your goal is to reproduce the source material provided by the user verbatim:

Format in Markdown:

- Reproduce the text of the source material without changing any text.

- Organize the text by closely following the original formatting and out in markdown formatting without the "```markdown```" fencing around the entire output.

- If the original text's formatting is broken after being extracted from the PDF, reorganize in the most logical way.

- Detect code snippet languages and use their code block fencing.

**IMPORTANT**:

- You will occasionally encounter odd formatting due to code or text extracted PDFs made from web pages that contained code playground elements.

- In these cases focus exclusively on the code itself and do not copy or pay special attention to any text from the code playground buttons.

- Detect the code snippet language and ensure proper code block fencing is used.

- For example, a LeetCode editorial page has a code playground with buttons to change the language, these may appear in the extracted text as a list of languages above the code, but you must ignore that list of languages and detect the language based on the code snippet itself.

Before you response, ensure the markdown formatting is complete and accurate.
"""


CONCEPTS_PROMPT = """
You will be provided source material text. Your goal is to exclusively extract all desirable items per my definition below:

Desirable Concept Items:
- Facts.
- Key concepts.
- Key words.
- Supporting details.
- Supporting concepts.

Undesirable Example Items:
- Examples.
- Comparative scenarios.
- Code snippets.
- Practical examples.
    
**DO NOT** Cross Contaminate Lists:
- Ensure concept items exist exclusively in the concepts list. **DO NOT** include undesirable example items.

Ensure Individual Self-Contained Items:
- Recursively break items down into self-contained parts.

Ensure Items In Markdown:
- Format each item in markdown.
"""


ABSENT_PROMPT = """
Source Material:
{SOURCE_MATERIAL}


Prompt:
You will be provided a list of concepts from the source material above. Your goal is to thoroughly search the source material for any desirable items that are absent in the provided list, and output a new list with everything included:

Desirable Concept Items:
- Facts.
- Key concepts.
- Key words.
- Supporting details.
- Supporting concepts.

Undesirable Example Items:
- Examples.
- Comparative scenarios.
- Code snippets.
- Practical examples.
    
Absent Items:
- Must exist in the source material, but are absent from the provided list.

Before you respond, ensure the new list you output includes all previous list items, and the absent items you discovered, with the items in markdown format.
"""


CONCEPT_MAP_PROMPT = """
You will be provided with source material text. Let's think step-by-step to deliver a detailed and engaging concept map of the source material. Output in markdown text.

Start by stating the title. If no title, sum up the content in less than four words without indefinite articles like "The". For example, "Java: Base Types"; "Java: This Keyword".

Describe elements in detail:

- Extract exact citations of all facts, key concepts, key words, supporting details, supporting concepts, comparative scenarios, code snippets, and practical examples.

- Recursively break elements down into self-contained components.

- Explain each component and how they interact. For example, "The process begins with X, which then leads to Y and results in Z."

- Break down the information logically. For instance, "Product A costs X dollars, while Product B is priced at Y dollars."

Focus on the content itself rather than the format:

- **DO NOT** include terms referring to the content format.

- **DO NOT** mention the content type. Instead, directly discuss the information presented.

- **DO NOT** include irrelevant details such as page numbers, metadata, or meta-information.

Keep your explanations comprehensive:

- Be exhaustive in describing the content, as your audience cannot see the original source material.

Engage with the content:

- Interpret and analyze the information where appropriate, offering insights to help the audience understand its significance.

------

Output format:

[TITLE]

[Content description]

- **DO NOT** include chapter or section numbers in the title.
"""


IMAGE_ANALYSIS_PROMPT = """
You will be provided with an image. Your goal is to deliver a detailed and engaging presentation about the content you see, using clear and accessible language suitable for a 101-level audience. Output in markdown format.

Start by stating the title. If no title, sum up the content in less than four words. For example, "Java Base Types"; "Java This Keyword".

Describe visual elements in detail:

- **Diagrams**: Explain each component and how they interact. For example, "The process begins with X, which then leads to Y and results in Z."
  
- **Tables**: Break down the information logically. For instance, "Product A costs X dollars, while Product B is priced at Y dollars."

Focus on the content itself rather than the format:

- **DO NOT** include terms referring to the content format.
  
- **DO NOT** mention the content type. Instead, directly discuss the information presented.

Keep your explanation comprehensive yet concise:

- Be exhaustive in describing the content, as your audience cannot see the image.
  
- Exclude irrelevant details such as page numbers or the position of elements on the image.

Use clear and accessible language:

- Explain technical terms or concepts in simple language appropriate for a 101-level audience.

Engage with the content:

- Interpret and analyze the information where appropriate, offering insights to help the audience understand its significance.

------

Output format:

[TITLE]

[Content description]

- **DO NOT** include chapter or section numbers in the title.
"""


FLASHCARD_PROMPT = """
Tags List:
{tags}

Concept Map:
{concept_map}

You will be provided with a list of Anki tags, a concept map, and a list of concept items. Your goal is to:

- Formulate a question and answer for each concept item in the list.

- Reproduce a relevant example that exists in the concept map. If no relevant example exists, use the empty string ("").

- Choose **ALL** broad and specific **RELEVANT** tags that apply to the content of the question and answer for this flashcard.

Before you respond, ensure there exists a flashcard for each and every concept item in the concepts list.
"""