import OpenAI from "openai";
const openai = new OpenAI();

// ANSI color codes
const YELLOW = "\x1b[93m";
const WHITE = "\x1b[97m";

//                                               Pricing (Input / Output) per 1M tokens
const GPT_O1_PREVIEW = "o1-preview";          // $15.00 / $60.00
const GPT_O1_MINI = "o1-mini";                // $3.00 / $12.00
const GPT_4O = "gpt-4o";                      // $2.50 / $10.00
const GPT_4O_MINI = "gpt-4o-mini";            // $0.150 / $0.600

async function getConcept(prompt) {
  const completion = await openai.chat.completions.create({
    model: GPT_4O_MINI,
    messages: [
      { 
        role: "system",
        content: [
          {
            "type": "text",
            "text": "You are a student with attention to detail.",
          }
        ]
      },
      { 
        role: "user", 
        content: [
          {
            "type": "text",
            "text": prompt
          }
        ]
      },
    ],
  });
  const conceptResponse = completion.choices[0].message.content;
  return conceptResponse;
}

async function makeQuestion(prompt) {
  const completion = await openai.chat.completions.create({
    model: GPT_4O_MINI,
    messages: [
      { 
        role: "system",
        content: [
          {
            "type": "text",
            "text": "You are a student with attention to detail.",
          }
        ]
      },
      { 
        role: "user", 
        content: [
          {
            "type": "text",
            "text": prompt
          }
        ]
      },
    ],
  });
  const questionResponse = completion.choices[0].message.content;
  return questionResponse;
}

(async () => {
  const MODEL = GPT_4O_MINI;
  const userInput = process.argv[2];

  const backPrompt = `
    <source>${userInput}</source>
    List each fact and concept that you can find from the source material provided above in <back> tags, and place all <back> items within a <cards> tag.
    <example_output>
    <cards>
      <back>Java allows a class definition to be nested inside the definition of another class.</back>
      <back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
      <back>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</back>
      <back>Nesting classes are valuable when implementing data structures.</back>
      <back>An instance of a nested class can represent a small portion of a larger data structure.</back>
      <back>A nested class can serve as an auxiliary class that helps navigate a primary data structure.</back>
    </cards>
    </example_output>
  `;

  const concept = await getConcept(backPrompt);
  console.log(`\n${YELLOW}${MODEL}: ${WHITE}`);
  console.log(`${concept}\n`);

  const frontPrompt = `
    <source>${concept}</source>
    Within <source> tags is your source material. For all items in <cards> pair each <back> with an intelligent question in <front> tags.
    <example_output>
    <cards>
      <front>What is the purpose of nesting classes in Java?</front>
      <back>Java allows a class definition to be nested inside the definition of another class.</back>
      <front>In what situation is it beneficial to nest a class inside another class?</front>
      <back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
      <front>How do nesting classes enhance encapsulation in Java?</front>
      <back>Nesting classes can help increase encapsulation and reduce undesired name conflicts.</back>
      <front>What advantages do nesting classes provide when working with data structures?</front>
      <back>Nesting classes are valuable when implementing data structures.</back>
      <front>How does an instance of a nested class relate to larger data structures?</front>
      <back>An instance of a nested class can represent a small portion of a larger data structure.</back>
      <front>What role can a nested class play in relation to a primary data structure?</front>
      <back>A nested class can serve as an auxiliary class that helps navigate a primary data structure.</back>
    </cards>
    </example_output>
  `;

  const question = await makeQuestion(frontPrompt);
  console.log(`\n${YELLOW}${MODEL}: ${WHITE}`);
  console.log(`${question}\n`);
})();
