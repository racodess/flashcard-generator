TEXT_FORMAT = {"type": "text"}


FLASHCARD_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "flashcards",
        "strict": True,
        "schema": {
            "type": "object",
            "required": ["flashcards"],
            "properties": {
                "flashcards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "front", "back", "example", "source", "image", "external_source", "external_page"],
                        "properties": {
                            "name": {"type": "string"},
                            "front": {"type": "string"},
                            "back": {"type": "string"},
                            "example": {"type": "string", "enum": [""]},
                            "source": {"type": "string", "enum": [""]},
                            "image": {"type": "string", "enum": [""]},
                            "external_source": {"type": "string", "enum": [""]},
                            "external_page": {"type": "integer", "enum": [1]},
                        },
                        "additionalProperties": False,
                    },
                }
            },
            "additionalProperties": False,
        },
    },
}


PLACEHOLDER_MESSAGE = "See below for assistant's analysis of the image:"


REWRITE_PROMPT = """
Your goal is to reproduce the source material provided by the user verbatim:

Format in Markdown:

- Reproduce the source material verbatim with the only changes being the new markdown formatting.

Before you response, ensure the markdown formatting is complete and accurate.
"""


BRAINSTORM_KNOWLEDGE_MAP_PROMPT = """
You will be provided with source material text. Let's think step-by-step to brainstorm a knowledge map of the source material. Output in markdown text.

Start by stating the title. If no title, sum up the content in less than four words. For example, "Java Base Types"; "Java This Keyword".

Brainstorm the Knowledge Map:

- Extract all facts, key concepts, key words, supporting details, supporting concepts, comparative scenarios, code snippets, and practical examples.

- Recursively them break down into individual elements.

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


BRAINSTORM_FLASHCARDS_PROMPT = """
You will be provided with a knowledge map. Let's think step-by-step to brainstorm how to populate the front, back, and example fields of your flashcards. Output in markdown text.

Ensure atomicity:

- Ensure one unit of knowledge per card.

Craft Clear and Specific Flashcards:

- Brainstorm 2 distinct versions of each question-answer-example structure. For instance, different perspectives of the same concept.

- Ensure questions are close-ended.

- Add comparative scenarios or code snippets exclusively from the source material in markdown code block fencing.

- **DO NOT** fabricate examples. If no matching example exists, use an empty string ("").

Exhaust the Knowledge Map:

- Ensure full coverage of every single entry of the knowledge map with flashcards has been achieved.

Example Brainstorm Structure:

- Flashcard {num}:
    - Version 1:
        - Front: ...
        - Back: ...
        - Example: ...
        
    - Version 2:
        - Front: ...
        - Back: ...
        - Example: ... 

"""


JSON_FLASHCARDS_PROMPT = """
You will be provided with a text analysis of flashcards. Your goal is to reproduce those flashcards in JSON format using a schema.

- Description of the flashcard JSON schema parameters:

    - name: A concise title.

    - front: A question.

    - back: The answer.

    - example: a pre-defined enum value.

    - source: a pre-defined enum value.
    
    - image: a pre-defined enum value.
    
    - external_source: a pre-defined enum value.
    
    - external_page: a pre-defined enum value.
"""