Below is an **updated** `README.md` reflecting the current state of the project, including how to run the app in both **host** and **Docker** modes, new chunk-merging logic, and the latest file-organization details. 

---

# Flashcard Generator

An automated pipeline that **analyzes local files or URLs** using Large Language Models (LLMs) to produce high-quality Anki flashcards. This tool helps you maintain a powerful study workflow by generating flashcards from virtually any text, PDF, or even images (via OCR-like logic). It also supports fetching and converting web content to flashcards, chunked for optimal cost and clarity.

---

## Table of Contents

1. [Key Features](#key-features)  
2. [Requirements](#requirements)  
3. [Setup](#setup)  
4. [Usage](#usage)  
   - [Running on Host](#running-on-host)  
   - [Running via Docker](#running-via-docker)  
   - [Automatic Mode Detection](#automatic-mode-detection)  
5. [Environment Variables](#environment-variables)  
6. [Directory and File Structure](#directory-and-file-structure)  
7. [Program Flow](#program-flow)  
8. [Chunk Merging Logic](#chunk-merging-logic)  
9. [Results](#results)  
10. [Cost and OpenAI Usage](#cost-and-openai-usage)  
11. [Troubleshooting](#troubleshooting)  
12. [License](#license)

---

## Key Features

1. **Host or Docker**  
   - Run locally using requirements.txt for setup.
   - Or run in Docker, as long as you have Python and Docker installed, for easy setup.

2. **Recursive Directory Scanning**  
   - Recursively scans subfolders (excluding any named `used-files`), automatically organizing processed files to avoid duplication.

3. **Chunk Merging for Efficiency**  
   - Merges smaller text chunks to reduce total LLM calls and cost. 

4. **File Classification**  
   - Detects if a file is `.txt`, PDF, image, or otherwise.  
   - `.txt` files are analyzed or used to fetch URLs.  
   - PDFs and images are both processed as image-based content, with plans to integrate PDF document segmentation in the near future.

5. **Metadata Support**  
   - Per-directory `metadata.yaml` can specify tags or headings to ignore.

6. **Anki Integration**  
   - Automatically adds:
     - Decks (enumerated as "Imported<num>" by default)
     - Note types using pre-defined note templates supporting two distinct flashcard types (see below).
     - Flashcards using the AnkiConnect add-on.
     - Reference material for flashcards (PDFs and images).
       - Copies files to Anki’s `collection.media` folder and the required `Ankifiles` folder for the add-on “pdf viewer and editor”.
       - Optionally generates reference PDFs (see below).

7. **Two Distinct Flashcard Flows**  
   - **Problem Flow** for step-by-step solutions to algorithmic problem-solving questions.  
   - **Concept Flow** for standard Q&A flashcards (with optional rewriting of content).

8. **Text Rewriting & Summaries**  
   - For unformatted plain text content, automatically rewrites or summarizes content to improve clarity before generating flashcards.
   - Capable of producing formatted PDFs of rewritten `.txt` plain text content with syntax highlighting.

9. **URLs in `.txt`**  
   - `.txt` files can list URLs. Each URL is fetched, parsed, and converted into well-structured flashcards.

---

## Requirements

- **Python 3.12+**
- **Anki** with add-ons:
  - [Anki](https://apps.ankiweb.net/).
    - [AnkiConnect](https://ankiweb.net/shared/info/2055492159) running (for direct flashcard imports).
    - [pdf viewer and editor](https://ankiweb.net/shared/info/319501851) for linking PDFs to flashcards.
    - [Markdown and KaTeX Support](https://ankiweb.net/shared/info/1087328706) already included in the app's Anki note templates.
- **Docker** (optional).  
  - Needed if you plan to run in a docker container using `--run-mode docker`.

On Windows/Mac/Linux, usage is straightforward when running on the host system or Docker, but you need to adjust paths in .env accordingly (Use Docker appropriate paths for Windows).

On WSL Linux, usage is less straightforward but possible in both host and Docker mode. In particular, adjust the AnkiConnect URL in .env or the Docker `run` command to be WSL Linux appropriate due to the way WSL Linux handles references to localhost.

The application has sample source material folders in `contents/`, including metadata files and test files within `used-files/`.
- **Note:** any files placed within `problem-solving/` are run using the "problem-solving" flow.

---

## Setup

1. **Clone or download** this repository:

   ```bash
   git clone https://github.com/username/flashcard-generator.git
   cd flashcard-generator
   ```

2. **Copy** the environment template and customize it:

   ```bash
   cp setup/.env.template .env
   ```
   - Fill in your details (e.g., `OPENAI_API_KEY`, `ANKI_CONNECT_URL`, etc.).
      - For Docker mode on Windows, use Docker appropriate paths.
   - Make sure `.env` is in the **root** of this project folder.

3. **Running on Host**:
   - If running directly on the host system, first install the Python dependencies. See "Usage" for more details.

      ```bash
      pip install -r setup/requirements.txt
      ```

4. **Running via Docker**:
   - If you want to run inside Docker, ensure **Docker** is installed and running. The script will automatically build an image if it doesn’t exist yet. See "Usage" for more details.

---

## Usage

All execution starts from `main.py`, which decides whether to run on the **host** or in **Docker**.

### Running on Host

1. **Navigate** to the project folder:

   ```bash
   cd /path/to/flashcard-generator
   ```

2. **Run**:

   ```bash
   python main.py --run-mode host
   ```

   - This calls `host.py` directly, processing files under the `INPUT_DIRECTORY` specified in your `.env`.  
   - Make sure your `.env` points to the **correct** `INPUT_DIRECTORY`.

### Running via Docker

1. **Navigate** to the project folder:

   ```bash
   cd /path/to/flashcard-generator
   ```

2. **Run**:

   ```bash
   python main.py --run-mode docker
   ```

   - This will build the image if needed (via `container.py`).  
   - It then runs a temporary container that calls `host.py` inside Docker.  
   - Make sure Docker is running and the paths in your `.env` are valid paths in your OS (for mounting directories).

### Automatic Mode Detection

If you **omit** the `--run-mode` parameter:
1. The app checks if it’s **already inside** Docker.
   - If yes, it just runs on host (`host.py`) because you’re already in a container.
2. If **not** in Docker, it checks if Docker is **installed** and available.
   - If Docker **is** available, it spins up the Docker container.
   - Otherwise, it defaults to host mode.

---

## Environment Variables

Your `.env` (which the script automatically loads) should include at least:

- **`OPENAI_API_KEY`** – Your OpenAI API key.  
- **`ANKI_CONNECT_URL`** – Typically `http://localhost:8765`, or `http://host.docker.internal:8765` if using Docker on Windows. WSL Linux users will require adjustments.
- **`INPUT_DIRECTORY`** – The folder on your host system containing files to be processed (e.g., `//c/Users/username/flashcard-generator/content` on Windows).  
- **`ANKI_COLLECTION_MEDIA_PATH`** – Path to Anki’s `collection.media` folder (e.g., `//c/Users/username/AppData/Roaming/Anki2/User 1/collection.media` on Windows).  
- **`PDF_VIEWER_MEDIA_PATH`** – Path to the “pdf viewer and editor” add-on directory (e.g. `//c/Users/username/Documents/Ankifiles` on Windows).

Sample `.env` (see above for examples of Docker appropriate Windows paths):

```
OPENAI_API_KEY=sk-xxxx...
ANKI_CONNECT_URL=http://localhost:8765 (or http://host.docker.internal:8765)
INPUT_DIRECTORY=/absolute/path/to/flashcard-generator/content
ANKI_COLLECTION_MEDIA_PATH=/absolute/path/to/Anki2/User 1/collection.media
PDF_VIEWER_MEDIA_PATH=/absolute/path/to/Ankifiles
```

> **Note**  
> - Always keep `.env` out of version control (as an entry within `.gitignore`) to protect sensitive credentials.
> - The `Ankifiles` directory gets created if it doesn't exist yet, but the app still needs your chosen path.
> - A new `_pdf_files` gets created in Anki's `collection.media` to keep your PDFs in one place.

---

## Directory and File Structure

Below is an **abbreviated** structure to help you locate key files:

```
flashcard-generator/
│
├── content/
│   ├── dsa/
│   ├── java/
│   ├── python/
│   ├── used-files/     # created automatically upon running the script
│       └──test/        # contains sample test files
│
├── setup/
│   ├── .env.template
│   └── requirements.txt
│
├── utils/
│   ├── file_utils.py
│   ├── flashcard_logger.py
│   ├── llm_utils.py
│   ├── importer.py
│   ├── models.py
│   ├── openai_generator.py
│   ├── prompts.py
│   ├── scraper.py
│   └── templates.py
│
├── main.py             # CLI entry point (host or Docker)
├── host.py             # Core scanning & processing logic
├── container.py        # Docker logic (build & run container)
├── .env                # Created by the user using .env.template in setup/
├── Dockerfile
└── README.md
```

Outside of this repo:
- **Anki** `collection.media/` directory  
- **Anki pdf viewer** `Ankifiles` add-on directory (for PDF viewer integration)

---

## Program Flow

1. **Launch** the script (either `--run-mode host` or `--run-mode docker`).  
2. **If Docker is chosen** (or auto-detected) and Docker is available:
   - The script builds/runs a container, then calls `host.py` **inside** that container.
3. **`host.py`**:
   - Loads environment variables from `.env`.
   - Points to your `INPUT_DIRECTORY`.  
   - Calls `process_directory(...)`.

4. **`process_directory(...)`**:
   - Creates a `used-files` folder (if it doesn’t exist) inside `INPUT_DIRECTORY`.  
   - Recursively scans subdirectories, skipping any named `used-files`.

5. **Files are classified**:
   - **`.txt`**:  
     - If it contains **URLs**, each URL is fetched and parsed into Markdown, then chunked.  
     - Otherwise, the `.txt` content is used directly.  
   - **Non-`.txt`** (PDF, image, etc.):  
     - Moved to `used-files` for backup, then copied to Anki’s `collection.media`.  
     - Passed to the LLM for interpretation (treated as image-based text).

6. **Flashcard Generation**:
   - Delegated to `generate_flashcards(...)` inside `openai_generator.py`.  
   - Splits content into sections or “chunks.”  
   - **Two flows**: “problem” (step-by-step) or “concept” (general Q&A).  
   - Optionally rewrites text with the LLM to improve clarity before generating Q&A.

7. **Anki Import** (`importer.py`):
   - Creates/ensures the target deck and note type exist (via AnkiConnect).  
   - Adds the newly generated flashcards to Anki.

8. **Completion**:
   - The script finishes once all subfolders and files are processed.  
   - The new flashcards, along with any reference PDFs, appear in Anki.

---

## Chunk Merging Logic

When text is extracted (from `.txt`, web content, or OCR-like processing), the code **merges smaller chunks** to reduce token usage and overall cost:

- **Minimum chunk size**: 300 tokens  
- **Maximum merged size**: ~1000 tokens  

Process:
1. Small chunks (< 300 tokens) get buffered until merging them would exceed ~1000 tokens.  
2. Once near the limit, the buffer is “flushed” into a single chunk.  
3. Large chunks (≥ 300 tokens) are kept as-is to ensure important content remains intact.

This approach drastically improves efficiency by avoiding too many short LLM calls.

---

## Results

**1. Text Files**  
- Rewritten/summarized content for clarity  
- Optionally generates a reference PDF placed directly in Anki’s media folder  
- Produces Q&A flashcards with your specified tags

**2. URL-Based**  
- Web content is scraped, converted to Markdown, chunked, and turned into structured flashcards.  
- Each heading becomes a chunk, further merged if it’s too small.

**3. PDFs & Images**  
- Processed as image-based text.  
- Potential for hallucinations if the PDF is large or poorly formatted, but short, well-structured documents work well.

**4. Metadata-Driven Tags**  
- `metadata.yaml` in each folder can specify `anki_tags` to add hierarchical tags in Anki (e.g., `DSA::Graphs::Basics`).

---

## Cost and OpenAI Usage

- **Text-based** operations typically use a cost-effective model, keeping usage fees minimal.  
- **PDF/Image-based** operations can cost more, since they require more tokens for the vision-based LLM.  
- Keep an eye on your [OpenAI Dashboard](https://platform.openai.com/account/usage) to monitor usage.  
- Provide your **OpenAI API key** in `.env`.

---

## Troubleshooting

- **.env file not found!**  
  Ensure `.env` is at the root of the project and has the correct environment variables.

- **Permission Denied on Directories**  
  Run the script with sufficient permissions for reading/writing the target directories.

- **Docker run fails**  
  Make sure Docker Desktop is installed, running, and that you’re mounting valid host paths in your `.env`.

- **Anki not receiving cards**  
  Check that Anki is open, and [AnkiConnect](https://ankiweb.net/shared/info/2055492159) is installed.  
  Validate `ANKI_CONNECT_URL` in `.env`.

- **Dependency errors**
  Hopefully Docker is a viable solution, but you may run into issues with poppler, weasyprint, or pdfminer especially on the host system. Review instructions for installing these dependencies on your system, consult an LLM if necessary, and consider using a virtual environment.

---

**Happy Flashcarding!** If you have any questions, feel free to open an issue or make a pull request.