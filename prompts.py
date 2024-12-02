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
                            "name": {"enum": [], "type": "string"},
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
- You are ChatGPT, a student AI who thinks step-by-step when responding to prompts.
- You are given source material from a textbook, article, or lesson that contains facts, concepts, code examples, and extraneous distracting information like metadata, and meta-information.
- Your exclusive focus is on the parameter requested by the user\'s prompt until otherwise instructed.
- Description of the JSON schema parameters:
    - name: a flashcard header pre-defined in the schema.
    - front: an empty string (e.g. "") until instructed otherwise.
    - back: an empty string (e.g. "") until instructed otherwise.
    - example: an empty string (e.g. "") until instructed otherwise.
    - source: an empty string (e.g. "") until instructed otherwise.
    """
}

CONCEPTS_PROMPT = """
**Prompt:**
- Let's think step-by-step, create a comprehensive list in plain markdown text of every single fact, key concept, and definition described in the source material:

**Important Guidelines:**

- Do **not** include code examples or code snippets.
- Ensure that all items in the list are self-contained without referring to external material by including context hooks that enforce a single strong specific connection.

Before you respond, please ensure that the list adheres to these guidelines.

**Source Material:**
{user_input}
"""

CHECK_PROMPT = """
**Prompt:**
Did you miss anything?
"""

RESTATE_PROMPT = """
**Prompt:**
- Let's think step-by-step, work within the original source material's overall context to restate and expound on the most recent response by using your external knowledge to make logical connections and asking yourself each of these important questions:

**Important Questions:**
- What? Explain the concept, tool, or technology.
- Why? Discuss why the concept is important or necessary.
- When? Identify situations or scenarios where the concept should be applied.
- Where? Indicate where in the codebase or architecture the concept is relevant.
- Who or What? Identify who or what uses or implements the concept.
- How? Describe how to use or apply the concept in practice, focusing on methodology without including code snippets or specific code examples.
"""

BACK_PROMPT = """
**Prompt:** 
- Your goal will be to create the backs of all the flashcards using every single fact, key concept, and definition: 

**Important Guidelines:** 
- Focus exclusively on each fact, key concept, or definition.
- Ensure the content on the back of the flashcard is self-contained and answerable without referring to external material by using context hook to make one explicit connection. 
- The content on the back of the flashcard is in plain markdown text without fencing.

**Example Assistant Output (The rest is excluded to save input tokens):**
{"flashcards":[{"name":"This Keyword","front":"","back":"In Java, `this` is a reference to the current instance of the class within a non-static method.","example":"","source":""},{"name":"This Keyword","front":"","back":"When a method is invoked (e.g., `thing.foo(a, b, c)`), `this` refers to the object that the method was called on, in this case, `thing`.","example":"","source":""},{"name":"This Keyword","front":"","back":"`this` can be used to store the current instance in a variable or pass it as an argument to another method that requires an instance of the class.","example":"","source":""},{"name":"This Keyword","front":"","back":"If a local variable has the same name as an instance variable, the local variable takes precedence. `this` allows access to the instance variable using dot notation (e.g., `this.variableName`).","example":"","source":""},
"""

FRONT_PROMPT = """
**Prompt:**
Lets think step-by-step, fill in the front of all cards.

**Example Assistant Output (The rest is excluded to save input tokens):**
{"flashcards":[{"name":"This Keyword","front":"What does the keyword `this` refer to in Java?","back":"In Java, `this` is a reference to the current instance of the class within a non-static method.","example":"","source":""},
"""

WORDINESS_PROMPT = """
**Prompt:**
Please reduce the unnecessary wordiness in the back field of each flashcard by rewriting the back into the shortest version of itself that you reasonably can without losing important details.
"""

FIND_EXAMPLES_PROMPT = """
**Prompt:** 
Let's think step-by-step, gather all examples in the source material and output them in markdown text by following these instructions and guidelines: 

**Instructions:** 
- Do not include the "```markdown\\n```" fencing. 
- Code snippets must be fenced in markdown code block fencing. 
- Code snippets separated in the source material must also be outputting in independent fencing in your response.
- Rewrite special characters in their markdown or html equivalent. 
- Preserve language specific formatting. 
- Gather all inline examples. 
- Gather all examples separate from bodies of text. 
- Gather any examples demonstrating syntax with generic naming.

**Guidelines:** 
- Look for keywords like 'example', 'syntax', 'as follows', 'such as', or some variation of that followed by a code snippet of some kind. 

**Examples of Various Assistant Outputs:**
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
**Prompt:**
Please insert each code section in your previous response into the example field of all relevant cards where applicable by preserving the code block fencing and the code formatting. It is acceptable and encouraged for multiple cards to share the same code snippet if applicable. 

**Example Assistant Output (only a partial example to save input tokens, your response will be much larger):**
{"flashcards":[ # beginning of this example excluded; only relevant entries remain below
{"name":"This Keyword","front":"In what scenario can `this` be used in constructors?","back":"`this` can be used to invoke another constructor within the same class, allowing for code reuse and proper initialization of instance variables.","example":"```java\npublic Counter(int count) {\n  this.count = count; // set the instance variable equal to parameter\n}\n```","source":""},{"name":"This Keyword","front":"How can `this` streamline constructor initialization?","back":"A zero-argument constructor can invoke a one-argument constructor by using `this`, passing a default value to streamline initialization.","example":"```java\npublic Counter() {\n  this(0); // invoke one-parameter constructor with value zero\n}\n```","source":""},{"name":"This Keyword","front":"What happens when local variables share names with instance variables?","back":"Local variables can mask instance variables when they share the same name, necessitating the use of `this` to refer to the instance variable explicitly.","example":"","source":""},{"name":"This Keyword","front":"What is unique about the syntax for calling constructors in Java?","back":"The syntax for calling a constructor is special in Java, where `this` is treated as a method to invoke another constructor.","example":"```java\nmodifiers name(type0 parameter0, ..., typen-1 parametern-1) {\n    // constructor body...\n}\n```","source":""},{"name":"This Keyword","front":"How is a Counter object instantiated?","back":"A Counter object can be instantiated using the constructor with an initial value.","example":"```java\nCounter d = new Counter(5);\n```","source":""},{"name":"This Keyword","front":"What does a zero-argument Counter constructor do?","back":"A zero-argument constructor creates a Counter with a default value of zero.","example":"```java\npublic Counter() {\n  // creates a counter with value zero\n}\n```","source":""}]}
"""

CITATIONS_PROMPT = """
**Prompt:**
Please fill in the source field of each card by explicitly citing the source material of where that fact, concept, or definition was found, including 2 sentences before the direct citation and 2 sentences after it, to ensure broad context. Before you respond, let's think step-by-step and make sure to adhere to the 2 sentence before and after the citation rule.
"""

REMOVE_BAD_QUESTIONS_PROMPT = """
**Prompt:**
Please remove any flashcards that explicitly ask the student to produce an example.
"""