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
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"


def get_completion(prompt: str, prefill=""):
    stream = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=1,
        stream=True,
        system="You are a student with attention to detail.",  # Response context
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": prefill}],
    )

    print(f"{MAGENTA}{MODEL}: {RESET}", end="", flush=True)

    input_tokens = 0
    for event in stream:
        if event.type == "message_start":
            input_tokens = event.message.usage.input_tokens

        elif event.type == "content_block_delta":
            content = event.delta.text
            print(f"{WHITE}{content}{RESET}", end="", flush=True)

        elif event.type == "message_delta":
            output_tokens = event.usage.output_tokens
            print(f"\n\nTotal tokens used (input + output): {input_tokens} + {output_tokens}", flush=True)

    print()


if __name__ == "__main__":
    USER_PROMPT = sys.argv[1]
    PREFILL = "<fact_concept>"

    PROMPT = f"""<source>{USER_PROMPT}</source>
    List each fact and concept that you can find from the source material provided above in <fact_concept> tags without changing the original text.
    Here is an example:
    <example>
    <fact_concept>Java allows a class definition to be nested inside the definition of another class.</fact_concept>
    <fact_concept>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</fact_concept>
    <fact_concept>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</fact_concept>
    </example>
    """

    get_completion(PROMPT, PREFILL)