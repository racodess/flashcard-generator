from dotenv import load_dotenv
from anthropic import Anthropic
import sys, os

load_dotenv()
my_secret = os.getenv("HIDE_THIS")
client = Anthropic(api_key=my_secret)

#                                      Cost(In/Out) per MTok |   Latency   |   Max Output   |   Vision   |   Batch API   |   Description
#                                                            |             |                |            |               |
# MODEL = "claude-3-opus-20240229"      # $15.00 / $75.00    |   Moderate  |   4096         |   Yes      |   Yes         |   Complex tasks & understanding
# MODEL = "claude-3-5-sonnet-20241022"  # $3.00  / $15.00    |   Fast      |   8192         |   Yes      |   Yes         |   Most intelligent & capable
# MODEL = "claude-3-sonnet-20240229"    # $3.00  / $15.00    |   Fast      |   4096         |   Yes      |   No          |   Balanced speed & intelligence
# MODEL = "claude-3-5-haiku-20241022"   # $1.00  / $5.00     |   Fastest   |   8192         |   No       |   Yes         |   Fastest intelligence
MODEL = "claude-3-haiku-20240307"  # $0.25  / $1.25          |   Fastest   |   4096         |   Yes      |   Yes         |   Fastest & most compact

# ANSI color codes
MAGENTA = "\033[95m"
WHITE = "\033[97m"

def get_concept(prompt, prefill=""):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        system="You are a student with attention to detail.",  # Response context
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": prefill}]
    )
    concept_response = response.content[0].text
    return concept_response


if __name__ == "__main__":
    user_input = sys.argv[1]
    tag = "<concept>"

    initial_prompt = f"""<source>{user_input}</source>
    List each fact and concept that you can find from the source material provided above in a {tag} tag.
    Here is an example:
    <example>
    <concept>
    - Java allows a class definition to be nested inside the definition of another class.
    - The main use for nesting classes is when defining a class that is strongly affiliated with another class.
    - Nesting classes can help increase encapsulation and reduce undesired name conflicts.
    </concept>
    </example>
    """

    concept = get_concept(initial_prompt, tag)
    print(f"{MAGENTA}{MODEL}: {WHITE}")
    print(f"{concept}")