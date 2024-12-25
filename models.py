from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict, ValidationError

class Extra(BaseModel):
    context: str = Field(
        description="In one comprehensive paragraph, paraphrase the context before and after the current concept in the source material without sacrificing the original terminology."
    )
    example: str = Field(
        description=(
            """
            **Please select the most accurate applicable code snippet, example, or comparative scenario concretely illustrates the concept:**
            - **Must exist** in the source material.
            - **Can be from any context** in the source material as long as it clearly applies to the current concept.
            - **If nothing clearly applies** fill this field with an empty string to maintain structure.
            - **Format in markdown**, especially the appropriate code block fencing for code snippets.
            """
        )
    )
    tags: List[str] = Field(
        description=(
            """
            A list of applicable Anki tags that reflect the hierarchy of knowledge and are selected exclusively from the given list of Anki tags.
            **DO NOT** create new tags that are absent from the given list of tags.
            **DO NOT** use external tags.
            """
        )
    )
    model_config = ConfigDict(extra='forbid')


class ConceptItem(BaseModel):
    concept: str = Field(
        description="The current concept item cited verbatim."
    )
    extra: Extra = Field(
        description="Contains all relevant information about the concept from the source material, including its context, an example if applicable, and the relevant list of Anki tags."
    )
    model_config = ConfigDict(extra='forbid')


class Concepts(BaseModel):
    concepts: List[ConceptItem] = Field(
        description="A list of concept items cited verbatim from the source material and formatted in markdown."
    )
    model_config = ConfigDict(extra='forbid')


class Content(BaseModel):
    front: str = Field(
        description=(
            """
            Paraphrase a clear and effective question that tests recall of the current concept item, in markdown format, by following the Anki best practices provided to you.
            """
        )
    )
    back: str = Field(
        description=(
            """
            Paraphrase a direct and concise answer to the question that tests recall of the current concept item in markdown by following the Anki best practices provided to you.
            Ensure the answer is fully consistent with the source material, does not repeat parts of the question, and stands on its own. 
            """
        )
    )
    model_config = ConfigDict(extra='forbid')


class FlashcardItem(BaseModel):
    content: Content = Field(
        description="The container for the finalized question and answer that test the key concept, carefully derived from the source material."
    )
    title: Literal[""]
    front: Literal[""]
    back: Literal[""]
    example: str = Field(
        description="The contents of the example field within the current concept's `extra` field. Represents the source material example tied to the current concept item, if one existed, otherwise an empty string "" for structural consistency."
    )
    image: Literal[""]
    external_source: Literal[""]
    external_page: Literal[""]
    tags: List[str] = Field(
        description = "The contents of the tags field within the current concept's `extra` field. Represents the relevant list of Anki tags chosen for the current concept item."
    )
    model_config = ConfigDict(extra='forbid')


class Flashcard(BaseModel):
    title: str = Field(
        description=(
            """
            Develop an accurate and succinct title in markdown. The title should follow the format `BroadTopic: SpecificConcept` (e.g., 'Java: Identifiers'). 
            Ensure the title directly references the information in the current list of concepts by being relevant, specific, and adherent to the source material's terminology.
            **DO NOT** use Anki tags or Anki tag formating to create the title.
            """
        )
    )
    flashcards: List[FlashcardItem] = Field(
        description=(
            """
            A list of flashcards derived from each and every single concept item in the list of concepts by following the provided Anki best practices for flashcards.
            Each FlashcardItem must reflect a crucial aspect of the concept, with well-formed front/back, source material example, and accurate Anki tags that best represent the item.
            """
        )
    )
    model_config = ConfigDict(extra='forbid')


class Restatement(BaseModel):
    restatement: str = Field(
        description=(
            """
            Think step-by-step to produce a concise restatement of the original LeetCode problem:
            
            1. Comprehend the Specifics: Grasp the details and requirements of the original problem.
            2. Abstract Core Components: Identify and generalize the key elements and constraints.
            3. Map to Standard Problems: Relate the abstracted problem to well-known algorithmic challenges.
            4. Formulate General Statement: Rephrase the problem in generalized terms that align with standard problems.
            
            - Ignore references to PDF artifacts, page numbers, or other extraneous text.
            
            - **Example:**
                - **Problem:** You are given a binary string s (a string containing only `0` and `1`). You may choose up to one `0` and flip it to a `1`. What is the length of the longest substring achievable that contains only `1`?
                - **Restatement:** Because the string can only contain `1` and `0`, another way to look at this problem is 'what is the longest substring that contains at most one `0`'?.
            """
        )
    )
    model_config = ConfigDict(extra='forbid')


class Step(BaseModel):
    step: str = Field(
        description="A step from the incremental drill-down for this approach, paraphrased from the source material in a succinct, fully clear, unambiguous manner."
    )
    pitfall: str = Field(
        description = "Key pitfall, boundary conditions, or tricky edge case to watch out for in this step. If none exists, use an empty string."
    )
    code: str = Field(
        description="All lines of code **in markdown code block fencing** from this approach's final implementation up to and including this step of the incremental drill-down **EVEN IF THE CODE IS NOT YET TECHNICALLY COMPLETE AT THIS STEP**."
    )
    model_config = ConfigDict(extra='forbid')


class ProblemFlashcardItem(BaseModel):
    title: str = Field(
        description=(
            """
            Think step-by-step to develop an accurate and succinct title in markdown.
            The title should follow the format `ProblemName: SpecificApproach` (e.g., 'Two Sum: Brute Force Approach'). 
            Ensure the title directly references the problem and current approach as it appears in the source material.
            **DO NOT** use Anki tags to create the title.
            """
        )
    )
    approach: str = Field(
        description = (
            """
            Identify and paraphrase the high-level logic of the approach (e.g., two-pointer, dynamic programming, etc.) from the source material currently being addressed.
            - Provide the conceptual overview, ignoring references to original headings or structural text from the source.
            """
        )
    )
    solution: str = Field(
        description="The complete formatted code for this approach, in markdown code block fencing, reproduced verbatim from the source material."
    )
    steps: List[Step] = Field(
        description=(
            """
            Think step-by-step to illustrate the incremental drilled-down logic that bridges the gap from the high-level logic of this approach to the final code implementation of this approach.
            - Show how each conceptual piece (data structures, loops, conditionals) fits into the final solution.
            - You **must** include the relevant piece of code, in fenced markdown code blocks, referencing only the essential lines from this approach's final implementation.
            """
        )
    )
    time: str = Field(
        description="The time complexity of this approach formatted in KaTeX."
    )
    time_explanation: str = Field(
        description="A comprehensive insightful explanation of the time complexity of this approach."
    )
    space: str = Field(
        description="The space complexity of this approach formatted in KaTeX."
    )
    space_explanation: str = Field(
        description="A comprehensive insightful explanation of the space complexity of this approach."
    )
    image: Literal[""]
    external_source: Literal[""]
    external_page: Literal[""]
    tags: List[str] = Field(
        description=(
            """
            A list of applicable Anki tags that categorize the problem. Chosen exclusively from the list provided to you. **DO NOT** invent new tags.
            Tags should reflect the hierarchy or domain of the knowledge selected exclusively from the given tags list.
            """
        )
    )
    model_config = ConfigDict(extra='forbid')


class ProblemFlashcard(BaseModel):
    problem: str = Field(
        description="Name of the problem. For example: 'Two Sum'"
    )
    url: str = Field(
        description="The exact URL of the algorithmic problem-solving question."
    )
    flashcards: List[ProblemFlashcardItem] = Field(
        description=(
            """
            The main container for these specialized LeetCode flashcard.
            - Contains each approach to the current problem from the source material.
            - Each approach contains the restatement of the problem, approach details, pitfalls, and Anki tags.
            """
        )
    )
    model_config = ConfigDict(extra='forbid')