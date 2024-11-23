import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";

const openai = new OpenAI();

const GPT_O1_PREVIEW = "o1-preview";   // $15.00 / $60.00 (Input / Output) per 1M tokens
const GPT_O1_MINI = "o1-mini";         // $3.00 / $12.00
const GPT_4O = "gpt-4o";               // $2.50 / $10.00
const GPT_4O_MINI = "gpt-4o-mini";     // $0.15 / $0.60

// ANSI color codes
const YELLOW = "\x1b[93m";
const WHITE = "\x1b[97m";

// Anki "Name" field
const NAME = "Java Primer";

const CardSchema = z.object({
  cards: z.array(
    z.object({
      name: z.literal(NAME),
      front: z.string(),
      back: z.string(),
    })
  )
});

function cleanJSONResponse(response) {
  return response.replace(/```json|```/g, '').trim();
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
      </cards>
    </example_output>
  `;

  const concept = await getCompletion(backPrompt);

  const frontPrompt = `
    <source>${concept}</source>
    Within <source> tags is your source material. For all items in <cards> pair each <back> with an intelligent question in <front> tags.
    <example_output>
      <cards>
        <front>What is the purpose of nesting classes in Java?</front>
        <back>Java allows a class definition to be nested inside the definition of another class.</back>
        <front>In what situation is it beneficial to nest a class inside another class?</front>
        <back>The main use for nesting classes is when defining a class that is strongly affiliated with another class.</back>
      </cards>
    </example_output>
  `;

  const frontAndBack = await getCompletion(frontPrompt);

  const finalPrompt = `
    Questions and concepts:
    ${frontAndBack}

    Reference the questions and concepts above to convert all of them from into a JSON object with a 'cards' array, each containing 'name', 'front', 'back'.

    - 'name' will always be ${NAME} and never change.
    - 'back' is the fact or concept.
    - 'front' is an intelligent question created for the concept in the 'back'.

    **Important:** Output only the JSON object. Do not include any code fences, markdown, or additional text.

    Example Output:
    {
      "cards": [
        {
          "name": "Java Primer",
          "front": "What is the purpose of nesting classes in Java?",
          "back": "Java allows a class definition to be nested inside the definition of another class.",
        },
        // Additional cards...
      ]
    }
  `;

  const structuredResponse = await makeJSON(finalPrompt);
  let stringifiedResponse = "";
  try {
    stringifiedResponse = JSON.stringify(structuredResponse, null, 2);
    console.log(`\n${YELLOW}${MODEL}: ${WHITE}\n`, stringifiedResponse);
  } catch (error) {
    console.error("Failed to get structured response:", error.message);
  }
})();

async function getCompletion(prompt) {
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
  const response = completion.choices[0].message.content;
  return response;
}

async function makeJSON(prompt) {
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

  const structuredResponse = completion.choices[0].message.content;
  const cleanedResponse = cleanJSONResponse(structuredResponse);

  try {
    const parsedResponse = CardSchema.parse(JSON.parse(cleanedResponse));
    return parsedResponse;
  } catch (error) {
    console.error("Validation Error:", error);
    throw new Error("Invalid response structure.");
  }
}
