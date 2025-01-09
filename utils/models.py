"""
Purpose:

- Contains Pydantic classes (`Flashcard`, `ProblemFlashcard`, etc.) that define the JSON schema for structured output from OpenAI API calls.


**Important Note:**

- Requires the use of client.beta.chat.completions.parse from the OpenAI API.
"""
from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict, ValidationError


class Data(BaseModel):
    image: Literal[""]
    external_source: Literal[""]
    external_page: Literal[""]
    url: Literal[""]


class ConceptItem(BaseModel):
    context: str = Field(
        description="One comprehensive paragraph of context for the concept item."
    )
    concept: str = Field(
        description="The current concept item cited verbatim from the source material."
    )
    example: str = Field(
        description="The applicable example (formatted in markdown with code block fencing for code snippets) that **must exist** and is reproduced verbatim as it appears in the concept map. **DO NOT** create your own examples. **DO NOT** use external examples."
    )
    tags: List[str] = Field(
        description="The list of Anki tags. **DO NOT** create your own tags. **DO NOT** use external tags."
    )
    model_config = ConfigDict(extra='forbid')


class Concepts(BaseModel):
    concepts: List[ConceptItem] = Field(
        description="A list of concept items cited verbatim from the source material and formatted in markdown."
    )
    model_config = ConfigDict(extra='forbid')


class Entity(BaseModel):
    entity: str = Field(
        description="An entity that exists in the source material."
    )
    relationship: str = Field(
        description="The relationship this entity has with another entity."
    )
    model_config = ConfigDict(extra='forbid')


class FlashcardItem(BaseModel):
    entities: List[Entity]
    front: str = Field(
        description="The question."
    )
    back: str = Field(
        description="The answer."
    )
    example: str = Field(
        description="The example."
    )
    data: Data
    tags: List[str] = Field(
        description="The Anki tags chosen exclusively from the list of Anki tags provided in the prompt."
    )
    model_config = ConfigDict(extra='forbid')


class Flashcard(BaseModel):
    flashcards: List[FlashcardItem] = Field(
        description="A list of flashcards derived from concept items."
    )
    header: str = Field(
        description=(
            """
            Describe the flashcards list using an accurate and succinct title in markdown format that follows the structure `BroadTopic: SpecificConcept` (e.g., 'Java: Identifiers'). 
            **DO NOT** use Anki tags or Anki tag formating to create the title.
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
    header: str = Field(
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
    data: Data
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
    problem_url: str = Field(
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