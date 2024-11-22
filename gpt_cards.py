from dotenv import load_dotenv
import openai
import sys, os

load_dotenv()
my_key = os.getenv("OPENAI_API_KEY")
openai.api_key = my_key

# ANSI color codes
MAGENTA = "\033[95m"
WHITE = "\033[97m"

#                                        Pricing (Input/Output)/1M tokens
GPT_O1_PREVIEW = "o1-preview"          # $15.00 / $60.00
GPT_O1_MINI = "o1-mini"                # $3.00 / $12.00
GPT_4_O = "gpt-4o"                     # $2.50 / $10.00
GPT_4_O_MINI = "gpt-4o-mini"           # $0.150 / $0.600

def get_concept(prompt, prefill=""):
    response = openai.ChatCompletion.create(
        model=GPT_4_O_MINI,
        max_tokens=1000,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a student with attention to detail."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": prefill}
        ]
    )
    concept_response = response['choices'][0]['message']['content']
    return concept_response

def make_question(prompt, prefill=""):
    response = openai.ChatCompletion.create(
        model=GPT_4_O_MINI,
        max_tokens=1000,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a student with attention to detail making flashcards."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": prefill}
        ]
    )
    question_response = response['choices'][0]['message']['content']
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
    print(f"{MAGENTA}{MODEL_NAME}: {WHITE}")
    print(f"{concept}")
    print()

    front_prompt = f"""
    <cards>{concept}
    For all items in <cards> pair each <back> with an intelligent question in <front> tags.
    Here is an example:
    <example>
    <cards>
    <front>What is the purpose of nesting classes in Java?</front>
    <back>Java allows a class definition to be nested inside the definition of another class.</back>
    <front>When is nesting classes most useful?</front>
    <back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
    <front>How does nesting classes help in Java programming?</front>
    <back>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</back>
    </cards>
    </example>
    """

    question = make_question(front_prompt, prefill)
    print(f"{MAGENTA}{MODEL_NAME}: {WHITE}")
    print(f"{question}")
    print()
