TEXT = {"type": "text"}

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
                        "required": ["name", "front", "back", "example", "source"],
                        "properties": {
                            "name": {"type": "string"},
                            "front": {"type": "string"},
                            "back": {"type": "string"},
                            "example": {"type": "string"},
                            "source": {"type": "string"},
                        },
                        "additionalProperties": False,
                    },
                }
            },
            "additionalProperties": False,
        },
    },
}

SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
- You are a top student who makes logical connections. You respond in plain markdown text when asked for text, or in JSON format when asked for a flashcard schema.

- Description of the flashcard JSON schema parameters:

    - name: a pre-defined header.
    
    - front: an empty string (e.g. "") until instructed otherwise.
    
    - back: an empty string (e.g. "") until instructed otherwise.
    
    - example: an empty string (e.g. "") until instructed otherwise.
    
    - source: an empty string (e.g. "") until instructed otherwise.
    """
}

INITIAL_PROMPT_IMG = """
You will be provided with an image of a PDF page or a slide. Your goal is to deliver a detailed and engaging presentation about the content you see, using clear and accessible language suitable for a 101-level audience.

If there is an identifiable title, start by stating the title to provide context for your audience.

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

If there is an identifiable title, present the output in the following format:

[TITLE]

[Content description]

- **DO NOT** include chapter or section numbers in the title.

- If there is no clear title, create the shortest and simplest title that sums up the content. For example, "Base Types"; "Throwing Exceptions"; "Creating and Using Objects"; "The Dot Operator".
"""

INITIAL_PROMPT_TEXT = """
Text being provided: ~~~
{TEXT}
~~~

You have been provided text from a textbook, article, lesson. Your goal is to deliver a detailed and engaging presentation about the content you see, using clear and accessible language suitable for a 101-level audience.

If there is an identifiable title, start by stating the title to provide context for your audience.

Describe elements in detail:

- **Diagrams**: Explain each component and how they interact. For example, "The process begins with X, which then leads to Y and results in Z."

- **Tables**: Break down the information logically. For instance, "Product A costs X dollars, while Product B is priced at Y dollars."

Focus on the content itself rather than the format:

- **DO NOT** include terms referring to the content format.

- **DO NOT** mention the content type. Instead, directly discuss the information presented.

Keep your explanation comprehensive yet concise:

- Be exhaustive in describing the content, as your audience cannot see the original content.

- Exclude irrelevant details such as page numbers or the position of elements on the original content.

Use clear and accessible language:

- Explain technical terms or concepts in simple language appropriate for a 101-level audience.

Engage with the content:

- Interpret and analyze the information where appropriate, offering insights to help the audience understand its significance.

------

If there is an identifiable title, present the output in the following format:

[TITLE]

[Content description]

- **DO NOT** include chapter or section numbers in the title.

- If there is no clear title, create the shortest and simplest title that sums up the content. For example, "Base Types"; "Throwing Exceptions"; "Creating and Using Objects"; "The Dot Operator".
"""

FRONT_BACK_PROMPT = """
Your goal is to create the front and back of all the flashcards using every single fact, key concept, and definition from the previous presentation: 

Important Guidelines: 

- Focus exclusively on each fact, key concept, or definition.

- Ensure the content on the front and back of the flashcard is self-contained and answerable without referring to external material by using context hook to make one explicit connection. 

- The content on the back of the flashcard is in plain markdown text without fencing.
"""

WORDINESS_PROMPT = """
Your goal is to reduce the unnecessary wordiness in the back field of each flashcard by rewriting the back into the shortest version of itself that you reasonably can without losing important details.
"""

FIND_EXAMPLES_PROMPT = """
Your goal is to gather all examples in the source material and output them in markdown text by following these instructions and guidelines: 

Instructions: 

- Do not include the "```markdown\\n```" fencing. 

- Code snippets must be fenced in markdown code block fencing. 

- Code snippets separated in the source material must also be outputting in independent fencing in your response.

- Rewrite special characters in their markdown or html equivalent. 

- Preserve language specific formatting. 

- Gather all inline examples. 

- Gather all examples separate from bodies of text. 

- Gather any examples demonstrating syntax with generic naming.

- Gather all examples from the presentation.

Guidelines: 

- Look for keywords like 'example', 'syntax', 'as follows', 'such as', or some variation of that followed by a code snippet of some kind. 

Examples of Various Assistant Outputs:

```java
public Counter(int count) {
  this.count = count; // set the instance variable equal to parameter
}
```

```java
public Counter() {
  this(0); // invoke one-parameter constructor with value zero
}
```

```java
modifiers name(type0 parameter0, ..., typen-1 parametern-1) {
    // constructor body...
}
```

```java
public Counter() {
}

public Counter(int initial) {
  count = initial;
}
```

```java
Counter d = new Counter(5);
```

```java
public Counter() {
  // creates a counter with value zero
}
```
"""

ADD_EXAMPLES_PROMPT = """
Your goal is to insert each code snippet in your previous response into the example field of all relevant cards where applicable by preserving the code block fencing and the code formatting. It is acceptable and encouraged for multiple cards to share the same code snippet if applicable. 

Example Assistant Output (only a partial example to save input tokens, your response will be much larger):

{"flashcards":[ # some entries excluded for brevity
{"name":"This Keyword","front":"In what scenario can `this` be used in constructors?","back":"`this` can be used to invoke another constructor within the same class, allowing for code reuse and proper initialization of instance variables.","example":"```java\npublic Counter(int count) {\n  this.count = count; // set the instance variable equal to parameter\n}\n```","source":""},{"name":"This Keyword","front":"How can `this` streamline constructor initialization?","back":"A zero-argument constructor can invoke a one-argument constructor by using `this`, passing a default value to streamline initialization.","example":"```java\npublic Counter() {\n  this(0); // invoke one-parameter constructor with value zero\n}\n```","source":""},{"name":"This Keyword","front":"What happens when local variables share names with instance variables?","back":"Local variables can mask instance variables when they share the same name, necessitating the use of `this` to refer to the instance variable explicitly.","example":"","source":""},{"name":"This Keyword","front":"What is unique about the syntax for calling constructors in Java?","back":"The syntax for calling a constructor is special in Java, where `this` is treated as a method to invoke another constructor.","example":"```java\nmodifiers name(type0 parameter0, ..., typen-1 parametern-1) {\n    // constructor body...\n}\n```","source":""},{"name":"This Keyword","front":"How is a Counter object instantiated?","back":"A Counter object can be instantiated using the constructor with an initial value.","example":"```java\nCounter d = new Counter(5);\n```","source":""},{"name":"This Keyword","front":"What does a zero-argument Counter constructor do?","back":"A zero-argument constructor creates a Counter with a default value of zero.","example":"```java\npublic Counter() {\n  // creates a counter with value zero\n}\n```","source":""}]}
"""

CITATIONS_PROMPT = """
Your goal is to fill in the source field of each card by explicitly citing the source material of where that fact, concept, or definition was found, including 2 sentences before the direct citation and 2 sentences after it, to ensure broad context. Before you respond, let's think step-by-step and make sure to adhere to the 2 sentence before and after the citation rule.
"""

REMOVE_BAD_QUESTIONS_PROMPT = """
Your goal is to remove any flashcards that explicitly ask the student to produce an example.
"""