import sys
import json
from openai import OpenAI
from prompts import (
    TEXT,
    FLASHCARD_SCHEMA,
    SYSTEM_MESSAGE,
    CONCEPTS_PROMPT,
    CHECK_PROMPT,
    RESTATE_PROMPT,
    BACK_PROMPT,
    FRONT_PROMPT,
    WORDINESS_PROMPT,
    FIND_EXAMPLES_PROMPT,
    ADD_EXAMPLES_PROMPT,
    CITATIONS_PROMPT,
    REMOVE_BAD_QUESTIONS_PROMPT,
)

# OpenAI Models
GPT_O1_PREVIEW = "o1-preview"  # $15.00 / $60.00 (Input / Output) per 1M tokens
GPT_O1_MINI = "o1-mini"        # $3.00 / $12.00
GPT_4O = "gpt-4o"              # $2.50 / $10.00
GPT_4O_MINI = "gpt-4o-mini"    # $0.15 / $0.60

# Use this model
MODEL = GPT_4O_MINI

# Get command line arguments
NAME_FIELD = sys.argv[1]
USER_INPUT = sys.argv[2]

# ANSI color codes for printing
GREEN = "\x1b[92m"
YELLOW = "\x1b[93m"
WHITE = "\x1b[97m"
MAGENTA = "\x1b[95m"

# Initialize the OpenAI client
client = OpenAI()

# Initialize the message list with the system message
message_list = [SYSTEM_MESSAGE]

def get_completion(model, prompt, response_format):
    # Add user's prompt to conversation history
    user_prompt = {"role": "user", "content": prompt}
    message_list.append(user_prompt)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=message_list,
            response_format=response_format,
            temperature=0.4, # 0 (deterministic) – 1 (creative)
            max_tokens=16383,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Print token usage
        print(f"{MAGENTA}{completion.usage}")

        assistant_response = completion.choices[0].message.content

        # Add model's response to conversation history
        assistant = {"role": "assistant", "content": assistant_response}
        message_list.append(assistant)

        return assistant_response
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def main():
    # Format prompt with variable containing source material from cmd line arg
    concepts_prompt = CONCEPTS_PROMPT.format(user_input=USER_INPUT)

    # Append name field from cmd line arg to schema
    FLASHCARD_SCHEMA['json_schema']['schema']['properties']['flashcards']['items']['properties']['name']['enum'].append(NAME_FIELD)

    prompts = [
        ("Concepts Prompt", concepts_prompt, TEXT),
        ("Check Prompt", CHECK_PROMPT, TEXT),
        ("Restate Prompt", RESTATE_PROMPT, TEXT),
        ("Back Prompt", BACK_PROMPT, FLASHCARD_SCHEMA),
        ("Front Prompt", FRONT_PROMPT, FLASHCARD_SCHEMA),
        ("Wordiness Prompt", WORDINESS_PROMPT, FLASHCARD_SCHEMA),
        ("Find New Examples Prompt", FIND_EXAMPLES_PROMPT, TEXT),
        ("Add New Examples Prompt", ADD_EXAMPLES_PROMPT, FLASHCARD_SCHEMA),
        ("Source Prompt", CITATIONS_PROMPT, FLASHCARD_SCHEMA),
        ("Remove Old Examples Prompt", REMOVE_BAD_QUESTIONS_PROMPT, FLASHCARD_SCHEMA),
    ]

    for title, prompt_text, response_format in prompts:
        # Print user's prompt
        print(f"\n{GREEN}User: \n{prompt_text}\n")

        # Get model's response
        response = get_completion(MODEL, prompt_text, response_format)

        # Change model's response string to formatted JSON
        if response_format == FLASHCARD_SCHEMA:
            try:
                response = json.dumps(json.loads(response), indent=4)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                sys.exit(1)

        # Print model's response
        print(f"\n{YELLOW}{MODEL}: {WHITE}\n{response}\n")

if __name__ == "__main__":
    main()