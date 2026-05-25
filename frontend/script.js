// script.js
// Frontend ↔ Backend connection.
//
// This file handles one operation:
//   ADD — POST /students → add a new student to the database
//
// The form submits name + juz to the FastAPI backend,
// which validates and stores it in SQLite.

"use strict";

// ---------------------------------------------------------------------------
// CONSTANTS
// ---------------------------------------------------------------------------

const API_URL              = "http://127.0.0.1:8000/students";
const FEEDBACK_DURATION_MS = 4000;


// ---------------------------------------------------------------------------
// DOM REFERENCES
// ---------------------------------------------------------------------------
const form       = document.getElementById("add-student-form");
const nameInput  = document.getElementById("student-name");
const juzSelect  = document.getElementById("student-juz");
const submitBtn  = document.getElementById("add-btn");
const feedbackEl = document.getElementById("feedback-area");


// ---------------------------------------------------------------------------
// UTILITY — FEEDBACK
// ---------------------------------------------------------------------------

/**
 * showFeedback()
 * Displays a message in the feedback area with the correct colour.
 *
 * @param {string}  message   - Text to display.
 * @param {"success"|"error"} type - Controls colour.
 * @param {boolean} autoClear - If true, hides after FEEDBACK_DURATION_MS.
 */
function showFeedback(message, type, autoClear = false) {
  feedbackEl.classList.remove("visible", "success", "error");
  feedbackEl.textContent = message;
  void feedbackEl.offsetHeight;                     // force reflow for CSS transition
  feedbackEl.classList.add("visible", type);

  if (autoClear) {
    setTimeout(() => {
      feedbackEl.classList.remove("visible", "success", "error");
    }, FEEDBACK_DURATION_MS);
  }
}

function hideFeedback() {
  feedbackEl.classList.remove("visible", "success", "error");
}


// ---------------------------------------------------------------------------
// UTILITY — BUTTON LOADING STATE
// ---------------------------------------------------------------------------

/**
 * setLoading()
 * Disables / re-enables the submit button while a request is in flight.
 * Prevents double-submissions.
 */
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  const btnText = submitBtn.querySelector(".btn-text");
  const btnIcon = submitBtn.querySelector(".btn-icon");

  if (isLoading) {
    btnText.textContent = "Submitting\u2026";
    btnIcon.textContent = "\u23F3";
  } else {
    btnText.textContent = "Add Progress";
    btnIcon.textContent = "\uFF0B";
  }
}


// ---------------------------------------------------------------------------
// MAIN — submitProgress()
//
// Flow:
//   1. Prevent page reload
//   2. Read + validate name and juz from form
//   3. POST { name, juz } to backend
//   4. Backend validates via Pydantic → INSERT INTO students
//   5. Show success or error message
//   6. Clear the form on success
// ---------------------------------------------------------------------------

/**
 * @param {Event} event - The form submit event.
 */
async function submitProgress(event) {
  event.preventDefault();   // stop the default browser page-reload

  const name = nameInput.value.trim();
  const juz  = parseInt(juzSelect.value, 10);

  // Client-side validation before hitting the network
  if (!name) {
    showFeedback("\u26A0\uFE0F  Please enter your name.", "error");
    nameInput.focus();
    return;
  }

  if (!juzSelect.value || isNaN(juz) || juz < 1 || juz > 30) {
    showFeedback("\u26A0\uFE0F  Please select a valid Juz (1\u201330).", "error");
    juzSelect.focus();
    return;
  }

  const payload = { name, juz };

  try {
    setLoading(true);
    hideFeedback();

    const response = await fetch(API_URL, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok) {
      // 201 Created — show success and clear the form
      showFeedback(`\u2705  ${data.name} added at Juz ${data.juz}!`, "success", true);
      nameInput.value = "";
      juzSelect.value = "";

    } else {
      // Server-side validation error (422) or other error
      const errorDetail = data?.detail
        ? (typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail))
        : `Server error (${response.status})`;

      showFeedback(`\u274C  ${errorDetail}`, "error");
    }

  } catch (networkError) {
    // fetch() itself failed — server unreachable
    console.error("Network error:", networkError);
    showFeedback(
      "\u274C  Could not reach the server. Make sure the backend is running on port 8000.",
      "error"
    );

  } finally {
    setLoading(false);  // always re-enable the button
  }
}


// ---------------------------------------------------------------------------
// EVENT LISTENER
// ---------------------------------------------------------------------------
form.addEventListener("submit", submitProgress);
