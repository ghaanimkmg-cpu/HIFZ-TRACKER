# database.py
# This file handles ALL database operations for the Hifz Tracker.
# It connects to the SQLite database, creates the students table,
# and provides functions for inserting, reading, and deleting students.
#
# Why a separate file?
# Keeping database logic separate from route logic (main.py) makes the
# code cleaner, easier to debug, and easier to expand later.

import sqlite3

# DATABASE_PATH is the location of our database file.
# Using a relative path means it will be created in the same folder
# as this file (i.e., backend/hifz.db).
DATABASE_PATH = "hifz.db"


def get_connection():
    """
    Opens and returns a connection to the SQLite database.

    sqlite3.connect() either:
    - Opens the existing hifz.db file (if it already exists), OR
    - Creates a brand new hifz.db file (if it doesn't exist yet)

    check_same_thread=False is needed because FastAPI uses async workers
    that may access the database from different threads.
    """
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)

    # Row factory: this makes SQLite return rows as Python dictionaries
    # instead of plain tuples. So instead of (1, "Ahmed", 5) we get
    # {"id": 1, "name": "Ahmed", "juz": 5} — much easier to work with.
    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    """
    Initializes the database by creating the students table if it doesn't exist.

    CREATE TABLE IF NOT EXISTS means:
    - First run: creates the table fresh
    - Every run after: sees the table already exists and does nothing
    This is safe to call every time the app starts.

    Column definitions:
    - id:   INTEGER PRIMARY KEY AUTOINCREMENT
            A unique number assigned automatically to each student.
            You never need to set this manually — SQLite handles it.
    - name: TEXT NOT NULL
            The student's name. TEXT means it stores characters/words.
            NOT NULL means this field cannot be left empty.
    - juz:  INTEGER NOT NULL
            The current Juz (1–30) the student is memorizing.
            Stored as a whole number.
    """
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL,
            juz  INTEGER NOT NULL
        )
    """)

    # commit() saves the change to the file permanently.
    # Without commit(), changes exist only in memory and are lost.
    conn.commit()
    conn.close()
    print("[OK] Database initialized. students table is ready.")


def add_student(name: str, juz: int) -> dict:
    """
    Inserts a new student into the students table.

    INSERT INTO students (name, juz) VALUES (?, ?)
    The ? placeholders are filled in safely by SQLite — this prevents
    SQL injection attacks (a common security vulnerability).

    After inserting, we fetch the new row back using lastrowid
    (the auto-generated id) so we can return the full student object.
    """
    conn = get_connection()

    cursor = conn.execute(
        "INSERT INTO students (name, juz) VALUES (?, ?)",
        (name, juz)
    )
    conn.commit()

    # Retrieve the newly inserted student so we can return it
    new_id = cursor.lastrowid
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (new_id,)
    ).fetchone()

    conn.close()

    # Convert the Row object to a plain dictionary before returning
    return dict(student)


def get_all_students() -> list:
    """
    Retrieves every student from the students table.

    SELECT * FROM students means "give me all columns for all rows."
    fetchall() returns every matching row as a list.
    """
    conn = get_connection()

    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    # Convert each Row object to a dictionary
    return [dict(row) for row in rows]


def delete_student(student_id: int) -> bool:
    """
    Deletes a student by their id.

    DELETE FROM students WHERE id = ?
    The ? is safely replaced with the student_id value.

    Returns True if a student was deleted, False if no student with
    that id was found (so the frontend can show an appropriate message).
    """
    conn = get_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    conn.commit()
    conn.close()

    # rowcount tells us how many rows were actually deleted
    return cursor.rowcount > 0
