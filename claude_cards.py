from dotenv import load_dotenv
from anthropic import Anthropic
import sys, os

load_dotenv()
my_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=my_key)

#                                                Cost(In/Out) per MTok |   Latency   |   Max Output   |   Vision   |   Batch API   |   Description
CLAUDE_3_OPUS = "claude-3-opus-20240229"          # $15.00 / $75.00    |   Moderate  |   4096         |   Yes      |   Yes         |   Complex tasks & understanding
CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"  # $3.00  / $15.00    |   Fast      |   8192         |   Yes      |   Yes         |   Most intelligent & capable
CLAUDE_3_SONNET = "claude-3-sonnet-20240229"      # $3.00  / $15.00    |   Fast      |   4096         |   Yes      |   No          |   Balanced speed & intelligence
CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"    # $1.00  / $5.00     |   Fastest   |   8192         |   No       |   Yes         |   Fastest intelligence
CLAUDE_3_HAIKU = "claude-3-haiku-20240307"        # $0.25  / $1.25     |   Fastest   |   4096         |   Yes      |   Yes         |   Fastest & most compact

# ANSI color codes
MAGENTA = "\033[95m"
WHITE = "\033[97m"

def get_concept(prompt, prefill=""):
    response = client.messages.create(
        model=CLAUDE_3_HAIKU,
        max_tokens=1000,
        temperature=0,
        system="You are a student with attention to detail.",  # Response context
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": prefill}]
    )
    concept_response = response.content[0].text
    return concept_response

def make_question(prompt, prefill=""):
    response = client.messages.create(
        model=CLAUDE_3_HAIKU,
        max_tokens=1000,
        temperature=0,
        system="You are a student with attention to detail making flashcards.",  # Response context
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": prefill}]
    )
    question_response = response.content[0].text
    return question_response

if __name__ == "__main__":
    user_input = sys.argv[1]
    prefill = "<cards>"

    back_prompt = f"""
    <source>{user_input}</source>
    List each fact and concept that you can find from the source material provided above in <back> tags, and place all <back> items within a {prefill} tag.
    Here is an example:
    <example>
    <cards>
    <back>Java allows a class definition to be nested inside the definition of another class.</back>
    <back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
    <back>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</back>
    </cards>
    </example>
    """

    concept = get_concept(back_prompt, prefill)
    print(f"{MAGENTA}{CLAUDE_3_HAIKU}: {WHITE}")
    print(f"{concept}")
    print()

    front_prompt = f"""
    <cards>{concept}
    For all items in <cards> pair each <back> with an intelligent question in <front> tags.
    Here is an example:
    <example>
    <cards>
    <front>...</front>
    <back>...</back>
    <front>...</front>
    <back>...</back>
    </cards>
    </example>
    """

    question = make_question(front_prompt, prefill)
    print(f"{MAGENTA}{CLAUDE_3_HAIKU}: {WHITE}")
    print(f"{question}")
    print()
