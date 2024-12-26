import sys

from rich.console import Console
from rich.pretty import Pretty, pprint

import importer
import models
import utils
import prompts

from openai import OpenAI

# OpenAI Models
GPT_O1_PREVIEW = "o1-preview"
GPT_O1_MINI = "o1-mini"
GPT_4O = "gpt-4o-2024-11-20"
GPT_4O_MINI = "gpt-4o-mini"

client = OpenAI()

console = Console()

def get_completion(file_type, model, message_list, response_format):
    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=message_list,
            response_format=response_format,
            max_completion_tokens=16384,
            temperature=0,
            top_p=0.1,
        )
        finish_reason = completion.choices[0].finish_reason
        if finish_reason != "stop":
            console.rule("[bold yellow] Finish Reason")
            console.print(
                f"Finished processing {file_type} with reason: {finish_reason}",
                style="yellow"
            )
        return completion
    except Exception as e:
        console.print(f"Error in processing {file_type}: ", Pretty(e, expand_all=True), style="red")
        sys.exit(1)


def handle_completion(system_message, user_message, response_format, file_type, run_as_image=False):
    message_list = [{"role": "system", "content": system_message}]

    utils.print_message("system", system_message, response_format, model=None, markdown=True)

    if run_as_image:
        model = GPT_4O
        content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{user_message}"
                }
            }
        ]
        utils.append_message("user", content, message_list)
        utils.print_message("user", prompts.PLACEHOLDER_MESSAGE, response_format, model=None, markdown=True)
    else:
        model = GPT_4O_MINI
        utils.append_message("user", user_message, message_list)
        utils.print_message("user", user_message, response_format, model=None, markdown=True)

    completion = get_completion(
        file_type,
        model=model,
        message_list=message_list,
        response_format=response_format,
    )

    utils.print_message("token", completion.usage, response_format, model=None, markdown=False)
    model = completion.model
    response = completion.choices[0].message.content

    if response_format is prompts.TEXT_FORMAT:
        utils.print_message("assistant", response, response_format, model, markdown=True)
    else:
        utils.print_message("assistant", response, response_format, model, markdown=False)

    return response


def fill_data_fields(flashcard_obj, file_name, file_type):
    for fc in flashcard_obj.flashcards:
        fc.data.image = file_name if file_type == "image" else ""
        fc.data.external_source = file_name if file_type != "image" else ""
        fc.data.external_page = 1


def generate_flashcards(collection_media_path, file_type, file_name, file_contents, tags, is_code):
    if is_code:
        problem_flashcard_prompt = prompts.PROBLEM_FLASHCARD_PROMPT.format(
            tags=tags
        )
        problem_flashcard_response = handle_completion(
            problem_flashcard_prompt,
            file_contents,
            models.ProblemFlashcard,
            file_type,
            run_as_image=True
        )
        problem_flashcard_model = models.ProblemFlashcard.model_validate_json(
            problem_flashcard_response
        )
        fill_data_fields(
            problem_flashcard_model,
            file_name,
            file_type
        )
        utils.print_message(
            "problem_flashcards",
            problem_flashcard_model,
            response_format=None,
            model=None,
            markdown=False
        )
        importer.add_flashcards_to_anki(
            problem_flashcard_model,
            template_name="AnkiConnect: Problem",
        )
    else:
        if file_type.lower() == "text":
            concept_map_response = handle_completion(
                prompts.CONCEPT_MAP_PROMPT,
                file_contents,
                prompts.TEXT_FORMAT,
                file_type
            )
            utils.create_pdf_from_markdown(
                collection_media_path,
                file_name,
                concept_map_response
            )
        else:
            concept_map_response = handle_completion(
                prompts.CONCEPT_MAP_PROMPT,
                file_contents,
                prompts.TEXT_FORMAT,
                file_type,
                run_as_image=True
            )
        concepts_list_prompt = prompts.CONCEPTS_LIST_PROMPT.format(
            tags=tags
        )
        concepts_list_response = handle_completion(
            concepts_list_prompt,
            concept_map_response,
            models.Concepts,
            file_type
        )
        concepts_list = utils.parse_llm_response(
            concepts_list_response
        )
        draft_flashcard_response = handle_completion(
            prompts.DRAFT_FLASHCARD_PROMPT,
            f"""
            #### List of each concept item to be addressed:
            {concepts_list}
            """,
            models.Flashcard,
            file_type
        )
        final_flashcard_response = handle_completion(
            prompts.FINAL_FLASHCARD_PROMPT,
            f"""
            #### The first draft of flashcards:
            {draft_flashcard_response}
            """,
            models.Flashcard,
            file_type
        )
        concept_flashcard_model = models.Flashcard.model_validate_json(
            final_flashcard_response
        )
        fill_data_fields(
            concept_flashcard_model,
            file_name,
            file_type
        )
        utils.print_message(
            "flashcard",
            concept_flashcard_model.flashcards,
            response_format=None,
            model=None,
            markdown=False
        )
        importer.add_flashcards_to_anki(
            concept_flashcard_model,
            template_name="AnkiConnect: Basic",
        )


def main():
    args = utils.get_args()

    file_path = args.file_path
    file_name = args.file_name
    collection_media_path = args.collection_media_path
    tags = args.tags
    is_code = args.code
    file_type = utils.detect_file_type(
        file_path
    )
    file_contents = utils.process_data(
        file_path,
        file_type
    )

    console.print(
        f"\nProcessing path: {file_path}"
    )
    console.print(
        f"\nProcessing file: {file_name}"
    )
    console.print(
        f"\nTags: \n{tags}"
    )

    generate_flashcards(
        collection_media_path,
        file_type,
        file_name,
        file_contents,
        tags,
        is_code,
    )


if __name__ == "__main__":
    main()