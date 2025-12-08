# Lecture Notes Generator MVP (Deepgram + Gemini)

This is a Minimum Viable Product (MVP) for a web application that takes an uploaded lecture audio file, transcribes it using **Deepgram**, and generates structured study notes using **Google Gemini**. This version is designed to be cost-effective, leveraging the free tiers of both services.

The project uses a **Python FastAPI** backend for the API logic and a **plain HTML/JavaScript** frontend for the user interface, making it easy to run locally, especially within an IDE like PyCharm.

## Project Structure

```
lecture-notes-mvp/
├── backend/
│   └── main.py           # FastAPI application logic (Deepgram + Gemini)
├── frontend/
│   └── index.html        # Frontend HTML, CSS, and JavaScript
├── requirements.txt      # Python dependencies
└── .env.example          # Template for environment variables
└── README.md             # This file
```

## Setup and Installation (PyCharm Instructions)

Follow these steps to set up and run the project in PyCharm.

### 1. Clone or Download the Project

Ensure you have the `lecture-notes-mvp` folder on your local machine.

### 2. Create a Virtual Environment

Open your terminal or use PyCharm's built-in terminal:

```bash
# Navigate to the project root directory
cd lecture-notes-mvp

# Create a new virtual environment (named 'venv')
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

**Security Note:** We use environment variables to securely handle your API keys, preventing them from being hardcoded into the source code.

1.  Copy the provided template file to create your configuration file:
    ```bash
    cp .env.example .env
    ```
2.  Open the newly created `.env` file and replace the placeholders with your actual API Keys.

    **`.env` file content:**
    ```
    # Get your key from: https://console.deepgram.com/
    DEEPGRAM_API_KEY="YOUR_SECRET_DEEPGRAM_API_KEY_HERE"

    # Get your key from: https://ai.google.dev/gemini-api/docs/api-key
    GEMINI_API_KEY="YOUR_SECRET_GEMINI_API_KEY_HERE"
    ```

### 5. Run the FastAPI Server

The backend is run using `uvicorn`, a high-performance ASGI server.

**Windows:**
```bash
# Run the server from the project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**
```bash
# Run the server from the project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start and be accessible at `http://localhost:8000`. The `--reload` flag is useful for development as it restarts the server automatically when code changes.

**Note:** You should see "Database initialized successfully." in the terminal output, which confirms the SQLite database has been created.

## Testing the Application

### 1. Access the Frontend

Open your web browser and navigate to:

[http://localhost:8000](http://localhost:8000)

The FastAPI application serves the `frontend/index.html` file on the root `/` route.

### 2. Test with a Sample Audio File

*   **How to get a test file:** You can easily record a short (e.g., 30-second) voice memo on your phone and transfer the `.m4a` or `.mp3` file to your computer.
*   **Upload and Process:**
    1.  Click the "Drag & Drop Audio File Here" area or drag your audio file onto it.
    2.  Click the **"Upload & Generate Notes"** button.
    3.  Observe the status messages change: "Uploading file..." -> "Processing: Transcribing and Summarizing...".
    4.  The results (Full Transcript and AI-Generated Notes) will appear below.

### 3. Expected JSON Response (Mock Example)

For a short, 30-second lecture on "The Importance of Virtual Environments in Python," the backend is expected to return a JSON response similar to this (mocked):

```json
{
  "status": "ok",
  "transcript": "Welcome to the quick lesson on Python virtual environments. They are crucial for managing dependencies, ensuring that each project has its own isolated set of libraries. This prevents conflicts and makes deployment much cleaner. Always use 'python -m venv venv' to create one and 'source venv/bin/activate' to start working.",
  "notes": "1. **One-Sentence Summary**: Python virtual environments are essential tools for isolating project dependencies, preventing conflicts, and ensuring clean deployment.\n2. **Key Takeaways**:\n*   Virtual environments provide isolated spaces for project dependencies.\n*   Isolation prevents conflicts between different projects' library versions.\n*   The standard way to create one is using `python -m venv venv`.\n*   Activation is done via `source venv/bin/activate` (or equivalent on Windows).\n*   Clean dependency management simplifies the deployment process.\n3. **Key Terms/Concepts**:\n*   Virtual Environment\n*   Dependency Management\n*   Isolation\n*   `venv` module\n*   Deployment\n4. **Follow-up Questions**:\n*   What are the differences between `venv` and other tools like `conda` or `pipenv`?\n*   How does a virtual environment interact with global Python packages?\n*   Describe a scenario where not using a virtual environment would cause a critical failure."
}
```

### 4. Testing the API Directly (cURL)

You can test the `/process-lecture` endpoint directly using `curl`. Replace `/path/to/your/audio.mp3` with the actual path to your test file.

```bash
curl -X POST "http://localhost:8000/process-lecture" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/audio.mp3;type=audio/mpeg"
```

## Functional Requirements and Implementation Details

| Feature | Implementation Detail |
| :--- | :--- |
| **Backend Framework** | Python FastAPI |
| **Transcription** | Deepgram API (`deepgram-sdk`) using `nova-2` model |
| **Summarization** | Google Gemini API (`google-genai`) using `gemini-2.5-flash` model |
| **File Handling** | `aiofiles` for asynchronous saving to a temporary directory (`/tmp`) |
| **Configuration** | `python-dotenv` to load `DEEPGRAM_API_KEY` and `GEMINI_API_KEY` from `.env` |
| **CORS** | Enabled for `*` (all origins) to allow local frontend development |
| **File Validation** | Checks for allowed MIME types and a maximum size of **20 MB** |
| **Frontend** | Minimal HTML, CSS, and JavaScript using `fetch` for API communication |
| **Error Handling** | Proper `try...except` blocks to catch API and file errors, returning a structured JSON error response. |

## Database

The application now includes a **SQLite database** (using SQLAlchemy) that automatically stores:
- All uploaded files with metadata (filename, size, type, timestamp)
- Generated transcripts
- Generated notes

**Features:**
- Automatic saving: Every successful upload is saved to the database
- History API: Access upload history via `GET /history`
- View previous uploads: Click any item in the history section to view its transcript and notes

The database file (`lecture_notes.db`) is created automatically in the project root on first run.

## Quick Start Guide

For detailed step-by-step instructions, see **[HOW_TO_RUN.md](HOW_TO_RUN.md)**.
