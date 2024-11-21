from dotenv import load_dotenv
from anthropic import Anthropic
import sys, os

load_dotenv()
my_secret = os.getenv("HIDE_THIS")

client = Anthropic()

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


def get_completion(prompt: str):
    stream = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=1,
        stream=True,
        system="You are a student with attention to detail.",  # Response context
        messages=[{"role": "user", "content": prompt}],
    )

    print(f"{MAGENTA}{MODEL}: {RESET}", end="", flush=True)

    for event in stream:
        if event.type == "message_start":
            input_tokens = event.message.usage.input_tokens
            print(f"Input tokens used: {input_tokens}", flush=True)
            print()

        elif event.type == "content_block_delta":
            content = event.delta.text
            print(f"{WHITE}{content}{RESET}", end="", flush=True)

        elif event.type == "message_delta":
            output_tokens = event.usage.output_tokens
            print()
            print(f"Output tokens used: {output_tokens}", flush=True)

    print()  # New line after the for event in stream:


if __name__ == "__main__":
    USER_PROMPT = sys.argv[1]

    PROMPT = f"""I will provide some text for you to find facts and concepts in.
        List all that you can find without changing the original text:

        <text>{USER_PROMPT}</text>
        """

    get_completion(PROMPT)