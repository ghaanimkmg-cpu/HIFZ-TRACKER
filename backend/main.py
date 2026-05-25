# main.py
# This is the entry point of the Hifz Tracker backend.
# It creates the FastAPI application, registers middleware, wires up
# the database, and defines all API routes (endpoints).

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import init_db, add_student, get_all_students, delete_student

# ---------------------------------------------------------------------------
# 1. Lifespan — startup logic
# ---------------------------------------------------------------------------
# The lifespan context manager is the modern way (FastAPI 0.93+) to run
# code on startup and shutdown. It replaces the deprecated @app.on_event.
# Everything BEFORE the `yield` runs on startup; after yield = shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()        # Runs once when the server starts
    yield            # Server is now running and handling requests
    # (add any cleanup code here if needed in the future)


# ---------------------------------------------------------------------------
# 2. Application instance
# ---------------------------------------------------------------------------
# FastAPI() creates the web application object.
# All routes, middleware, and events are attached to this object.
app = FastAPI(title="Hifz Tracker API", version="1.0.0", lifespan=lifespan)


# ---------------------------------------------------------------------------
# 2. CORS Middleware — Cross-Origin Resource Sharing
# ---------------------------------------------------------------------------
# Browsers block requests between different origins by default
# (e.g., your frontend on file:// talking to localhost:8000).
# This middleware tells FastAPI: "allow all origins" so the frontend
# can freely communicate with the backend during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins (safe for local dev)
    allow_methods=["*"],   # Allow GET, POST, DELETE, etc.
    allow_headers=["*"],   # Allow all request headers
)




# ---------------------------------------------------------------------------
# 4. Pydantic model — request body validation
# ---------------------------------------------------------------------------
# Pydantic is FastAPI's built-in validation library.
# When a POST request arrives, FastAPI automatically parses the JSON body
# and checks it against this model BEFORE our code even runs.
#
# Field(...)  — the value is REQUIRED (no default)
# min_length=1  — name cannot be an empty string ""
# ge=1, le=30   — juz must be >= 1 AND <= 30
#
# If validation fails, FastAPI automatically returns HTTP 422 Unprocessable
# Entity with a clear error message — the backend never crashes.
class StudentIn(BaseModel):
    name: str = Field(..., min_length=1, description="Student's full name")
    juz:  int = Field(..., ge=1, le=30,  description="Current Juz (1–30)")


# ---------------------------------------------------------------------------
# 5. ROUTES
# ---------------------------------------------------------------------------

# --- GET /students ----------------------------------------------------------
# Returns every student in the database as a JSON array.
#
# Example response:
# [
#   {"id": 1, "name": "Ahmed",  "juz": 5},
#   {"id": 2, "name": "Bilal",  "juz": 12}
# ]
#
# GET means "give me data" — it does not change anything in the database.
@app.get("/students")
def route_get_students():
    """Return all students stored in the database."""
    students = get_all_students()   # calls database.py → SELECT * FROM students
    return students                  # FastAPI serialises the list to JSON automatically


# --- POST /students ---------------------------------------------------------
# Adds a new student to the database.
#
# The client sends a JSON body like:
#   {"name": "Ahmed", "juz": 5}
#
# FastAPI validates it against StudentIn BEFORE this function runs:
#   • name must not be empty
#   • juz must be 1–30
# If validation fails → HTTP 422 returned automatically (no crash).
#
# On success → HTTP 201 Created + the new student object (with its auto id).
@app.post("/students", status_code=201)
def route_add_student(student: StudentIn):
    """Add a new student. Validates name (non-empty) and juz (1–30)."""
    new_student = add_student(student.name, student.juz)  # INSERT INTO students
    return new_student


# --- DELETE /students/{id} --------------------------------------------------
# Deletes the student whose id matches the URL path parameter.
#
# Example:   DELETE /students/3   → deletes the student with id = 3
#
# If the id doesn't exist in the database, we return HTTP 404 Not Found
# instead of silently doing nothing — good API practice.
@app.delete("/students/{student_id}")
def route_delete_student(student_id: int):
    """Delete a student by their id. Returns 404 if id not found."""
    deleted = delete_student(student_id)   # DELETE FROM students WHERE id = ?

    if not deleted:
        # delete_student() returns False when rowcount == 0
        # meaning no row matched that id — tell the client explicitly.
        raise HTTPException(
            status_code=404,
            detail=f"No student found with id {student_id}"
        )

    return {"message": f"Student {student_id} deleted successfully"}


# ---------------------------------------------------------------------------
# 6. Root health-check
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """Quick health-check — confirms the backend is alive."""
    return {"message": "Backend running"}
