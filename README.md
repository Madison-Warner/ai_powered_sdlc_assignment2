# Study Helper Web Application

A locally hosted study helper web application with a Python backend, local storage, quiz engine, and RAG retrieval.

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open your browser at `http://127.0.0.1:5000`.

## Features

- **Subject Management**: Create and manage study subjects.
- **Topic Organization**: Organize flashcards and study material under topics.
- **Flashcard System**: Create and review flashcards with weak score tracking.
- **Study Material Upload**: Upload text-based study materials for RAG retrieval.
- **Quiz Engine**: Generate quizzes from flashcards with spaced repetition.
- **RAG Retrieval**: Retrieve relevant definitions from study material using keyword search.
- **Local Storage**: All data stored locally in JSON format.

## Project structure

- `app.py` — Flask application entrypoint and API routes.
- `storage.py` — Local JSON persistence layer and CRUD operations.
- `quiz_engine.py` — Quiz generation and grading logic.
- `rag_retrieval.py` — Local RAG retrieval for definitions.
- `templates/index.html` — Main frontend HTML page.
- `static/style.css` — Frontend styling.
- `static/app.js` — Frontend JavaScript for API interactions.
- `data/storage.json` — Generated local data store.

## API Endpoints

### Subjects
- `GET /api/subjects` — List all subjects
- `POST /api/subjects` — Create a subject
- `GET /api/subjects/<id>` — Get subject details
- `PUT /api/subjects/<id>` — Update subject
- `DELETE /api/subjects/<id>` — Delete subject

### Topics
- `GET /api/topics?subject_id=<id>` — List topics for a subject
- `POST /api/topics` — Create a topic
- `GET /api/topics/<id>` — Get topic details
- `PUT /api/topics/<id>` — Update topic
- `DELETE /api/topics/<id>` — Delete topic

### Flashcards
- `GET /api/flashcards?topic_id=<id>` — List flashcards for a topic
- `POST /api/flashcards` — Create a flashcard
- `GET /api/flashcards/<id>` — Get flashcard details
- `PUT /api/flashcards/<id>` — Update flashcard
- `DELETE /api/flashcards/<id>` — Delete flashcard

### Study Material
- `GET /api/study-materials?topic_id=<id>` — List study materials for a topic
- `POST /api/study-materials` — Upload study material
- `GET /api/study-materials/<id>` — Get study material details
- `DELETE /api/study-materials/<id>` — Delete study material

### Quizzes
- `POST /api/quizzes/generate` — Generate a quiz for a subject
- `POST /api/quizzes/submit` — Submit quiz answers and get score

### RAG Retrieval
- `POST /api/rag/retrieve` — Retrieve definitions from study material

### Quiz Results
- `GET /api/quiz-results` — List all quiz results
- `POST /api/quiz-results` — Create a quiz result

## Frontend Features

The web application includes a complete frontend interface with the following capabilities:

- **Subject Management**: Create, view, edit, and delete subjects
- **Topic Organization**: Create topics under subjects with full CRUD operations
- **Flashcard Management**: Create and manage flashcards with questions and answers
- **Study Material Upload**: Upload text-based study materials for RAG retrieval
- **Interactive Quizzes**: Generate and take quizzes with multiple choice questions
- **Results Tracking**: View quiz scores and performance history
- **Responsive Design**: Works on desktop and mobile devices

## Usage

1. Start the Flask server: `python app.py`
2. Open `http://127.0.0.1:5000` in your browser
3. Use the navigation buttons to switch between different sections
4. Create subjects first, then topics, flashcards, and study materials
5. Generate quizzes and track your learning progress

## Deployment

This application is intended for local deployment using Python. It can also be run behind a production WSGI server if desired.

### Local deployment

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the application:

```powershell
python app.py
```

4. Open your browser at `http://127.0.0.1:5000`.

### Environment variables

- `PORT` — port to serve the application on (default: `5000`).
- `STORAGE_PATH` — path to the JSON storage file.
- `FLASK_ENV` — set to `development` for development mode.
- `FLASK_DEBUG` — set to `1` to enable Flask debug mode.

### Production server

For a more production-ready setup, install `gunicorn` and run:

```powershell
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

> Note: `gunicorn` is optional and not required for local testing.

## Testing

Run the full test suite with:

```powershell
python -m pytest tests/ -v
```

All tests should pass when the application is configured correctly.

## Notes

- The app stores all data locally in `data/storage.json`.
- The storage layer automatically initialises the JSON schema on first run.
- Frontend uses vanilla JavaScript with fetch API for all backend communication.
