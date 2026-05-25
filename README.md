# Hifz Progress Tracker

A full-stack web application for tracking student Quran memorization (Hifz) progress.

## Tech Stack

| Layer     | Technology         |
|-----------|--------------------|
| Frontend  | HTML, CSS, Vanilla JS |
| Backend   | Python + FastAPI   |
| Database  | SQLite (via sqlite3) |

## Project Structure

```
hifz-tracker/
│
├── backend/
│   ├── main.py          ← FastAPI application & routes
│   ├── database.py      ← SQLite connection & queries
│   ├── requirements.txt ← Python dependencies
│   └── hifz.db          ← SQLite database file (auto-created)
│
├── frontend/
│   ├── index.html       ← UI structure
│   ├── style.css        ← Styling
│   └── script.js        ← Frontend logic & fetch() calls
│
└── README.md
```

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open: http://127.0.0.1:8000

## Opening the Frontend

Open `frontend/index.html` directly in your browser.
