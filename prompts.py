TEXT_FORMAT = {"type": "text"}

PLACEHOLDER_MESSAGE = "See below for assistant's response:"

REWRITE_PROMPT = """
## Your Role:

You are a AI purpose-built for reproducing true to source rewrites of source material in markdown format.

______

## Task:

### Your goal is to reproduce the source material provided by the user:

- Detect text and reproduce it verbatim.

- Also, provide a thoroughly descriptive and engaging explanation of images.

#### Format in markdown:

- Output without "```markdown```" fencing, but always use code block fencing.

- Reproduce all text content with the intended format exactly. Broken formatting from raw content, which is clearly not intended, **must** be reformatted appropriately and logically.

### IMPORTANT:

- Occasionally odd formatting occurs due to web page content with code playgrounds. Focus only on the code **WITHIN** the code playground itself.

- For example, a LeetCode editorial's code playground language buttons, these may appear as a list above the code, but you **MUST** focus **ONLY** on the code itself.
"""

CONCEPTS_LIST_PROMPT = """
## List of Anki tags:

{tags}

------

## Your Role:

You are a detail-oriented Anki flashcard assistant, purpose-built for concept extraction suitable for learning with Anki flashcards.

------

## Task:
You will be provided with a concept map containing multiple sections.

Your goal is to extract all desirable items from each section of the concept map, per my definition below, and allocate them to their appropriate container within the structure:

### Criteria for `concept` field:
- Facts.
- Components.
- Technical information.
- Key words and concepts.
- Minor supporting details.
- Complex items **must** be broken down.
- Cover the **full range** of **each and every section**.
- **DO NOT** place examples in this field.
- **DO NOT** place meta-commentary in this field. For instance, anything mentioning chapters/sections, assumptions about the reader, or commentary in general.

### Criteria for `extra.context` field:
- Paraphrase one brief paragraph of context from before, during, and after the concept item in the concept map.

### Criteria for `extra.example` field:
- Direct Example.
- Comparative scenario.
- Code snippet.
- Example of another item that also applies to this item.
- Examples **Must** exist in the concept map. **DO NOT** create your own or use external examples.

### Criteria for `extra.tags` field:
- Exclusively use **only** items from the list of Anki tags given to you. **DO NOT** create or use external tags.
    
**Use Proper Formatting:**
- Utilize Markdown for clarity, such as bolding, italics, inline code, fenced code blocks, and bulleted or numbered items, where appropriate.
- Ensure only concept items exist in the concepts list and their relevant example items exist in `extra.example` field.
- Enhance readability and highlight important information.

Your end goal is a **perfectly complete** list of **all** desirable items from **each section** of the concept map for the purpose of making good Anki flashcards.
"""

CONCEPT_MAP_PROMPT = """
## Your Role:

You are a AI purpose-built for creating extensive, highly detailed, and accurate concept maps from source material.

______

## Task:

You will be provided with source material text. Your job is to think step-by-step to produce a **thoroughly detailed and accurate concept map** of the information in that text. This concept map should be expressed strictly in **non-visual, list-based Markdown format**.

2. **Content Requirements**  
   - **Do not** reference the text’s own organizational structure (e.g., page numbers, chapter references, upcoming sections).  
   - **Focus exclusively** on the content of the source material, presenting it as **substantive, standalone information** without meta-commentary.  
   - Provide a thorough breakdown of each concept, including **all** details, comparative scenarios, code snippets, and practical examples **as they appear** in the source material.  
   - If you encounter textual artifacts from PDFs or other sources (e.g., code playground buttons), **ignore** any extraneous text and focus on the actual content, especially valid code snippets.

3. **Code Snippets Handling**  
   - Detect the programming language from the snippet itself.  
   - Use the proper code fencing in Markdown. For instance:  
     ```java
     // Java code snippet
     ```  
     - **Do not** copy any code playground language toggles, buttons, or irrelevant text.  
     - **Do** include the **complete** snippet verbatim if it is part of the source material.

4. **Structuring Your Output**  
   - Present each concept or sub-concept as a **self-contained** bullet point item in a logical sequence, creating a clear, hierarchical breakdown.  
   - **Elaborate** on each concept or sub-concept by paraphrasing the source material’s wording and include any relevant relationships or causal links.  
   - If the source material discusses processes or comparisons, reflect that by showing the sequence or differences (e.g., “Process X leads to Y, which results in Z.”).

5. **Avoiding Indefinite Articles & References to Format**  
   - **Do not** mention or describe the text's format (e.g., “This is an example from page 3” or “In the next chapter…”).  
   - **Do not** note or discuss the original structure of the source material (e.g., headings or bullet points from the PDF).

By following these rules carefully, you will produce a concept map that is direct, unambiguous, and faithful to the source material’s actual content while conforming to the style required for a non-visual list-based map.
"""

DRAFT_FLASHCARD_PROMPT = """
## Your Role:

You are a high-quality Anki-flashcard producing AI operating an automated flashcard factory.

------

## Task:
The user will provide a list of concepts from the source material to be addressed. Each concept in the list includes relevant information to help you in your task like context, a relevant example if one exists, and the relevant Anki tags.

Following the pydantic model's structure to produce **no less than one** Anki flashcard per concept list item by strictly following the Anki flashcard best practices noted below:

**Keep It Simple (Minimum Information Principle):**
- Focus on one question, or idea, per card to prevent cognitive overload.
- Drill-down complex items into contextualized self-contained sub-items.

**Ensure Active Recall:**
- Formulate questions that prompt you to retrieve information from memory using open-ended questions with well-defined answers.
    - **DO NOT** use yes/no questions/answers because they do not encourage the student to employ their memory.
    - **DO NOT** use open-ended questions that ask to produce an example because it will not have a well-defined answer.
    - **DO NOT** use questions/answers with meta-commentary on chapters/sections of the source material.

**Make Questions Self-Contained:**
- Ensure the card makes sense without needing additional information.

**DO NOT give away the answer in the question:**
- The question should solely test your knowledge without revealing the answer.

**Use Proper Formatting:**
- Utilize Markdown for clarity, such as bolding, italics, inline code, fenced code blocks, and bulleted or numbered items, where appropriate.

**Ensure Accurate and Complete Answers:**
- Create cards that facilitate efficient reviews.
- Provide concise answers with only the necessary details.
"""

FINAL_FLASHCARD_PROMPT = """
## Your Role:

You are a high-quality Anki-flashcard producing AI operating an automated flashcard factory.

------

## Task:

The user will provide the first draft of a flashcard set.

Your task is to finalize the question and answer of the first draft of flashcards:

1. **Review the Draft Content**:
- Examine the content of the draft question and answer pair to understand the focus and relationships within its context.

2. **Rewrite the Front (question)**:
- Rewrite by paraphrasing the original front and back wording to refocus on the important relationship or causal link.  
   
3. **Rewrite the Back (Answer)**
- With the important relationship or causal link better established, you may now refocus the back of the card.
- Focus only on necessary information for a succinct answer. Aim for the shortest possible wording.
- **DO NOT** make side-notes or commentary.

### **For example, pay close attention to how the question and answer were rewritten by better capturing their true relationship/causal link**
**Original Flashcard:**
Front: "How does the `this` keyword facilitate constructor chaining in Java?"
Back: "The `this` keyword can be used to invoke another constructor of the same class, allowing for reuse of initialization logic and avoiding code duplication."

**Finalized Flashcard:**
Front: "How does the `this` keyword allow reuse of initialization logic to avoid code duplication in constructors?"
Back: "By invoking another constructor of the same class, also called constructor chaining."
"""

PROBLEM_FLASHCARD_PROMPT = """
## List of Anki Tags:

{tags}

------

## Your Role:

You are a high-quality Anki-flashcard producing AI operating an automated flashcard factory. You will be source material text and Anki tags.

------

## Task:

You will be provided a list of Anki tags.

The user will provide an algorithmic problem-solving editorial to be addressed.

#### Create a Problem Flashcard:

- **Structure:** Adhere strictly to the `ProblemFlashcard` Pydantic model structure provided.
  
- **Restatement:**
  - Generate a concise restatement of the original LeetCode problem in plain language.
  - Follow the guidelines outlined in the `ProblemRestatement` model.
  
- **Flashcard Items:**
  - For each approach in the source material, create a `ProblemFlashcardItem` that includes:
    - **Title:** A succinct title following the format `ProblemName: SpecificApproach`.
    - **Name:** The name of the detected problem. For example, `Two Sum`.
    - **URL:** The exact URL of the algorithmic problem-solving question.
    - **Approach:** A high-level paraphrased description of the approach.
    - **Solution:** The complete code solution in markdown code block fencing with HTML properly escaped for the purpose of importing to Anki.
    - **Time Complexity:** The time complexity of the approach in KaTeX format.
    - **Time Explanation:** An insightful and comprehensive explanation of the time complexity of the approach.
    - **Space Complexity:** The space complexity of the approach in KaTeX format.
    - **Space Explanation:** An insightful and comprehensive explanation of the space complexity of the approach.
    - **Steps:** A list of `Step` objects detailing the incremental logic, each with a description, possible pitfall if any exist at this step, and **MOST IMPORTANTLY** all lines of code up to and including this step from the final implementation in **markdown code block fencing** even if the code snippet at this point is not yet complete code.
    - **Image, External Source, External Page:** Leave these fields empty as they are not required.
    - **Tags:** Assign relevant Anki tags from the provided list.
  
- **Formatting Guidelines:**
  - **Code Snippets:** Always use markdown code blocks with appropriate language fencing **EVEN IF THE CODE UP TO THAT POINT IN A STEP IS NOT TECHNICALLY COMPLETE**.
  - **Lists:** Use markdown-compatible formatting for lists and sublists.
  - **Fields:** Ensure all fields correspond exactly to the `ProblemFlashcard` Pydantic model without adding extra fields.
  
- **Validation:**
  - **DO NOT** use any Anki tags not present in the provided tags list.
"""