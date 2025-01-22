# README

## Program Flow

1. **Run the Script:**  
   Invoke the application by running:
   ```bash
   python main.py /path/to/your/files
   ```
   This entry point is defined in `main.py`. It determines your operating system, locates the Anki `collection.media` folder, and prepares to process the provided directory.

2. **Directory Setup:**  
   `process_directory(...)` creates a `used-files` folder inside the specified directory if one does not already exist. This folder prevents files from being processed multiple times.

3. **Recursive Scanning:**  
   `_process_directory_recursive(...)` explores all subfolders, skipping any named `used-files`. It collects files (excluding `metadata.yaml`) and subdirectories for further processing.

4. **File Classification & Processing:**
   - **If the file is `.txt`:**  
     - The script scans each line to check if it contains a URL.  
       - **If a URL is detected:**  
         The code fetches the webpage content and converts it to Markdown. It then splits the Markdown by headings to create flashcards in smaller chunks.  
       - **If no URLs are found:**  
         The `.txt` is treated as plain text. A high-quality PDF of this text is generated for study reference.  
   - **If the file is NOT `.txt`:**  
     - This includes PDFs and images.  
     - The file is first moved to `used-files` (as a backup) and then copied to Anki’s `collection.media` folder.  
     - The script then infers its content type (image, PDF, etc.) and calls `generate_flashcards(...)`, which in turn imports the new flashcards to Anki.  
     - **Note:** Currently, PDFs are processed as images to simplify handling.

5. **Flashcard Generation (`generate_flashcards`):**  
   - Determines the flashcard “type” (`problem` or `general/concept`) based on file location or user metadata.  
   - **Problem Flow:** Uses a specialized prompt for step-by-step solutions (ideal for algorithmic or math problems).  
   - **Concept Flow:** Generates conceptual question-and-answer flashcards, often preceded by rewriting or summarizing text for clarity.  
   - Once generated, the flashcards go to Anki via the import process.

6. **Anki Import (`importer.py`):**  
   - Ensures the correct Anki note type (or template) exists, creating it if necessary.  
   - Ensures the target deck exists, creating a default “ImportedX” deck if none was specified.  
   - Adds the newly created flashcards through AnkiConnect’s `addNotes` action.

7. **Completion:**  
   The script terminates once all discovered files have been processed. Your new flashcards (and any reference PDFs) will then be visible in your Anki collection.

---

## Features

- **Automated File Handling**  
  Automatically classifies files as text, PDF, or image. Moves them into the `used-files` folder and copies them to the Anki `collection.media` folder without user intervention.

- **Recursive Directory Scanning**  
  Recursively scans subfolders (excluding `used-files`), preventing reprocessing of previously handled files.

- **Metadata Support**  
  Honors `metadata.yaml` in each folder to apply custom tags (`anki_tags`) or ignore specific headings (`ignore_sections`).

- **URL Extraction**  
  `.txt` files can be lists of URLs; each URL is fetched, parsed, and converted into targeted flashcards. Perfect for web articles, documentation, or blog posts.

- **Two Distinct Flashcard Flows**  
  - **Problem Flow** for step-by-step or algorithmic Q&A.  
  - **Concept Flow** for more general question-and-answer cards.

- **Integrated PDF Generation**  
  When text content is detected, the system can generate a clean PDF for study reference, placed directly in Anki’s media folder.

- **AnkiConnect Integration**  
  Automatically creates new decks and custom note types (if needed) via AnkiConnect, ensuring minimal setup for the user.

- **Text Rewriting**  
  Optionally rewrites text for clarity before flashcard generation, using an LLM prompt specifically designed for improving or summarizing text.

- **LLM Flexibility**  
  - Large text flows through GPT-4o-mini for cost-effectiveness.  
  - Images (including PDFs as images) are analyzed by GPT-4o to handle visual context.  

---

## Results

**Text Files**  
- Plain-text content, such as lecture notes or short articles, typically transforms into concise Q&A flashcards. Generating additional study aids—like a PDF of notes—makes reviewing more convenient.

**Web Content**  
- For `.txt` files containing URLs, web content is parsed into Markdown and then subdivided by headings. This approach produces well-structured flashcards, especially for longer articles or documentation pages.

**PDFs and Images**  
- PDFs are currently processed as images, enabling GPT-4o to visually interpret them. This can produce high-quality flashcards for documents originally designed as PDF textbooks or single-page images.  
- For very large PDFs-as-images, partial or inaccurate interpretations can occur (i.e., “hallucinations”). However, short or well-structured PDF pages generally yield good results.

**Metadata-Driven Tagging**  
- By specifying `anki_tags` in `metadata.yaml`, the application can attach hierarchical tags to your flashcards. This allows for flexible and organized review sessions in Anki (e.g., `Language::Python::Basics`).

---

## Cost

While the application itself is open-source and free to use, it relies on the OpenAI API for text and image interpretation:

1. **Text Processing**  
   Leveraging GPT-4o-mini for standard text analysis typically keeps costs low. On average, a few text files cost just a few cents USD.

2. **Image/PDF Processing**  
   GPT-4o handles images and PDFs (processed as images). It incurs a higher token usage but generally still remains affordable. For users processing large volumes of images or extensive documents, costs can accumulate.

3. **Key Management**  
   You must supply your own OpenAI API key. Ensure you monitor your usage in the OpenAI dashboard to track expenditure.

In most everyday usage scenarios, the costs remain minimal while providing substantial convenience and deeper learning through well-structured flashcards. If many large images or comprehensive PDFs are processed in bulk, plan your API usage accordingly.

---