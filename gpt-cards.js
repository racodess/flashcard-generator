from openai import OpenAI
client = OpenAI()

// ANSI color codes
const MAGENTA = "\x1b[95m";
const WHITE = "\x1b[97m";

//                                               Pricing (Input / Output) per 1M tokens
const GPT_O1_PREVIEW = "o1-preview";          // $15.00 / $60.00
const GPT_O1_MINI = "o1-mini";                // $3.00 / $12.00
const GPT_4O = "gpt-4o";                      // $2.50 / $10.00
const GPT_4O_MINI = "gpt-4o-mini";            // $0.150 / $0.600

async function getConcept(prompt, prefill = "") {
  const response = await openai.createChatCompletion({
    model: GPT_4O_MINI,
    max_tokens: 1000,
    temperature: 0,
    messages: [
      { role: "system", content: "You are a student with attention to detail." },
      { role: "user", content: prompt },
      { role: "assistant", content: prefill },
    ],
  });
  const conceptResponse = response.data.choices[0].message.content;
  return conceptResponse;
}

async function makeQuestion(prompt, prefill = "") {
  const response = await openai.createChatCompletion({
    model: GPT_4O_MINI,
    max_tokens: 1000,
    temperature: 0,
    messages: [
      { role: "system", content: "You are a student with attention to detail making flashcards." },
      { role: "user", content: prompt },
      { role: "assistant", content: prefill },
    ],
  });
  const questionResponse = response.data.choices[0].message.content;
  return questionResponse;
}

(async () => {
  const MODEL_NAME = GPT_4O_MINI;
  const userInput = process.argv[2];
  const prefill = "<cards>";

  const backPrompt = `
<source>${userInput}</source>
List each fact and concept that you can find from the source material provided above in <back> tags, and place all <back> items within a ${prefill} tag.
Here is an example:
<example>
<cards>
<back>Java allows a class definition to be nested inside the definition of another class.</back>
<back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
<back>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</back>
</cards>
</example>
`;

  const concept = await getConcept(backPrompt, prefill);
  console.log(`${MAGENTA}${MODEL_NAME}: ${WHITE}`);
  console.log(`${concept}`);
  console.log();

  const frontPrompt = `
<cards>${concept}
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
`;

  const question = await makeQuestion(frontPrompt, prefill);
  console.log(`${MAGENTA}${MODEL_NAME}: ${WHITE}`);
  console.log(`${question}`);
  console.log();
})();
