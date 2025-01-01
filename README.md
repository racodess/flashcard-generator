## Program Flow:
1. You run: `python main.py /path/to/files`.
2. `main.py` picks up that directory, determines your OS, finds the Anki `collection.media` folder, then calls `process_directory(...)`.
3. `process_directory(...)` sets up a `used-files` folder in that directory to store processed files as back-ups.
4. `_process_directory_recursive(...)` recursively walks subdirectories, skipping `used-files` so you don’t re-process the same files.
5. For each file:
   - If `.txt`, tries to see if it’s a list of URLs. If so, each URL gets fetched; the text from those URLs is fed to the LLM to create flashcards header-by-header (to avoid overloading the LLM).
       - If the `.txt` does not contain a list of URLs, it’s processed normally (see below) as plain-text and a high-quality PDF of notes is created out of the information for reference when studying the flashcards.

   - If NOT a `.txt` file (PDF or image file), calls `process_file(...)` → moves the file to `used-files` → copies it to Anki's media folder to link the file to flashcards → identifies content type → calls `generate_flashcards(...)` → imports flashcards to Anki.
       - Currently all PDFs are run as images for simplicity.
       - Images are currently analyzed by GPT-4o.

   - All text (and prompts after initial image analysis by GPT-4o) is handled by GPT-4o-mini.
6. `generate_flashcards`:
   - If `flashcard_type=='problem'`, it calls a specialized LLM prompt for “problem flashcards” (like algorithmic or step-by-step solutions).
   - Else does a concept-based flow: concept map → concept list → draft set of flashcards → final set of flashcards.
   - In all cases, once the flashcards are ready, it calls `importer.add_flashcards_to_anki(...)`.
7. In `importer.py`, the system ensures the correct "note type" (Anki terminology for a flashcard template) exists in Anki, ensures there’s a deck to put them in, then calls `addNotes` via AnkiConnect.
8. The script ends with the new flashcards created in your Anki collection.


## Results:
   - PDF files that were originally a PDF (e.g. textbook pages) provide good results.
   - PDF files that were NOT originally a PDF (e.g. a webpage saved or printed to PDF) provide poor results, therefore the URL feature is available.
       - Currently, all PDFs are run as images for simplicity.

   - Images are analyzed by GPT-4o and provide good results, but run up costs if many images are run.
       - GPT-4o-mini handles images at x33 the token use and slightly higher price on average than GPT-4o, therefore GPT-4o is delegated to handle all images.
       - Very large images can result in hallucinations (e.g. a large single-page PDF of an entire web page ran as an image).

   - All text (and prompts after initial image analysis by GPT-4o) is handled by GPT-4o-mini and produces good results.
       - Large quantities of text generally produces good results.
       - The more context, the better the results (e.g. the entire text from a textbook page, or under one header).
       - Content with minimal context (e.g. trying to make flashcards out of notes) produces poor results.)


## Cost:
- The application itself is free and open-source.
- All costs are due to OpenAI API key use, which is required by this application.
    - For just text, usually about 1-4 files/cent in USD.
    - For images, usually about 1-2 files/cent in USD.