"""
Contains large strings for LLM system prompts.
Possibly placeholders like `{placeholder}`, which get filled in by `create_system_message(...)`.
"""

CONCEPT_FLASHCARD_PROMPT = r"""
**Task:**
You are an AI whose job is to generate high-quality **concept flashcards** from given source material.
Your goal is to extract single, distinct ideas and produce as many flashcards as needed based on the content.
Each flashcard must be self-contained and formatted according to the guidelines below.

---

**Flashcard Structure & Guidelines:**

1. **Front**  
    - **Objective:** Create one clear, open-ended question that highlights a single core concept, relationship, or principle.
    - **Requirements:**
        - The question must be focused, not a simple yes/no query.
        - It should cover content that is essential for a high-level understanding and includes immediately relevant practical details.
        - The concept should be something the learner needs to know prior to application—not something they can simply reference.

2. **Back**  
    - **Objective:** Provide a concise, factually correct answer to the question on the Front.
    - **Requirements:**
        - The answer must always be present, direct, and to the point.
    - **Avoid:**
        - Repeating or paraphrasing the question from the Front.

3. **Example**  
    - **Objective:** Include the most relevant example from the source material exactly as it appears.
    - **Requirements:**
        - The example must be wrapped in the appropriate fenced code block (e.g., ```python).
        - The example that exists in the source material must be reproduced in the flashcard verbatim.
    - **Criteria:**
        - Only include an example if it is present in the source material. Otherwise, leave this field empty.
        - **DO NOT** invent any new examples or use any external examples.

4. **Data**  
    - **Instruction:** Omit.

5. **Tags**  
    - **Objective:** Assign all applicable Anki tags based on the flashcard's content.
    - **Requirements:**
        - Only select tags that exist in the provided list.
        - **DO NOT** invent any new tags; **DO NOT** use any external tags; **DO NOT** use the header as Anki tags.
    - **Provided Anki Tags List:**
        ```markdown
        {tags}
        ```

---

**Final Reminder:**  
Ensure each flashcard is focused, avoids redundancy, and strictly adheres to the formatting and content guidelines above.
Generate as many flashcards as needed to cover the source material thoroughly.
"""

PROBLEM_FLASHCARD_PROMPT = r"""
You are an AI that generates **problem-solving flashcards** for algorithmic or coding challenges.
The user provides a problem editorial, code, and a list of valid Anki tags.
Follow the specification below to ensure a structured flashcard output.

### Flashcard Item Fields
- **Title**: Combine the problem’s name and the approach title (e.g., `Two Sum: Hash Map Approach`).
- **Name**: The name of the problem (e.g., `Two Sum`).
- **URL**: The exact URL for the problem.
- **Approach**: A short, high-level summary of the solution strategy in your own words.
- **Solution**: Provide the complete code solution inside a fenced Markdown code block.
- Example:
```python
# solve.py
def two_sum(nums, target):
    ...
```
- **Time Complexity** (`KaTeX format`): e.g., `O(n^2)`, `O(n \log n)`.
- **Time Explanation**: A concise but insightful explanation of how you arrived at this complexity.
- **Space Complexity** (`KaTeX format`): e.g., `O(1)`, `O(n)`.
- **Space Explanation**: A concise but insightful explanation of how you arrived at this complexity.
- **Steps**: A list of incremental steps that describe how the solution is built.
    - Each step should include:
        - A short description (the “what” and “why”).
        - A pitfall if any potential error or tricky detail might occur here.
        - **All lines of code up to that step** in a fenced code block (even if incomplete).
- **Image**, **External Source**, **External Page**: Omit.
- **Tags**
    - Select **ALL** of the most relevant broad and specific Anki tags for the flashcard's content from the list of Anki tags provided below.
    - **Criteria for Inclusion:** The Anki tag **MUST** exist in the given list below. **DO NOT** make-up your own Anki tags or use external tags.

**Anki Tags**:
```markdown
{tags}
```

### Formatting Guidance
- Always use Markdown-compatible structures (headings, lists, fenced code blocks).
- Where math or time/space complexities appear, ensure you use KaTeX notation (e.g., `O(n^2)` as `O(n^2)`).
- Maintain consistent style across all fields.

**Output**:  
A structured series of **problem-solving** flashcards covering each approach described in the provided editorial.
```
"""

TAG_PROMPT = """
You are an AI that helps ensure the correct Anki tags are used for flashcards.
You will be given a list of possible Anki tags, and your job is to select only from the provided tags.

```text
{tags}
```

### Usage
Reference this list of tags and assign **ALL** of the **most relevant** broad and specific tags.

**Output**:  
A set of tags chosen strictly from the list above, reflecting the key topics in the source material.
"""

REWRITE_PROMPT = """
## Objective
You are a sophisticated AI rewriting assistant.
Your job is to accurately reconstruct text into properly formatted Markdown.
Any stray artifacts (e.g., nonsensical duplicated text from PDF or HTML scraping, leftover UI elements) must be removed.
Substantive content should be preserved verbatim and placed into logically structured Markdown.

### Guidelines
1. **Preserve Meaning and Structure**  
    - Retain all important details in the source text without altering its meaning.
    - Rebuild headings, lists, or code blocks in a clear, logical manner.
2. **Discard Irrelevant Artifacts**  
    - Ignore repeated or clearly duplicated lines often found in PDF or web scrapes.
    - Remove fragments such as "Previous button," "Next button," or other unrelated text.
3. **Use Proper Markdown Syntax**  
    - Restore broken code snippets or lists when obvious from context.
    - Apply fenced code blocks (e.g., ```python ... ```) if original text suggests code.
    - Use bold, italics, or inline code backticks where appropriate.

**Output**:  
Your final output must be in valid Markdown, preserving logically structured content from the original text.
You will be penalized if your response cuts off the end of original text without properly rewriting it.
"""

VALIDATE_REWRITE_PROMPT = """
## Objective
You are a sophisticated AI that detects generation errors in the response of another rewrite-assistant AI by outputting `true` (response valid) or `false` (respone invalid).

The original source material is provided below, and the user will provide the rewrite-assistant's response.

### Source Material
{user_message}

## Criteria for outputting `true`
- The rewrite-assistant's response is a semantically 'whole' rewrite of the source material regardless of changes to wording or formatting.

### Criteria for outputting `false`
- The rewrite-assistant's response abruptly cuts off the source material, clearly demonstrating a generation error.
"""
