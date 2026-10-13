import os
import json
from pathlib import Path
from datetime import datetime

import streamlit as st

from config import MAX_RETRIES
from generator import generate_lesson
from evaluator import evaluate_lesson
from memory import save_attempt, load_memory, get_learning_summary

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
LOG_FILE = OUTPUT_DIR / "rejection_log.json"

st.set_page_config(
    page_title="LessonAI Studio",
    page_icon="📘",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1180px;}
    .hero {
        padding: 1.35rem 1.5rem; border-radius: 18px;
        background: linear-gradient(120deg, #14213d 0%, #243b67 100%);
        color: white; margin-bottom: 1.1rem;
    }
    .hero h1 {margin: 0; font-size: 2rem;}
    .hero p {margin: .4rem 0 0 0; color: #dbeafe;}
    .small-muted {color: #64748b; font-size: .9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>📘 LessonAI Studio</h1>
      <p>Generate · Evaluate · Improve — a self-evaluating lesson content system</p>
    </div>
    """,
    unsafe_allow_html=True,
)

api_ready = bool(os.getenv("GEMINI_API_KEY"))
top1, top2, top3 = st.columns(3)
top1.metric("Generator", "Gemini API")
top2.metric("Evaluation", "Rule-based rubric")
top3.metric("Maximum attempts", str(1 + MAX_RETRIES))
if api_ready:
    st.success("Gemini API key detected in this terminal session.")
else:
    st.warning(
        "GEMINI_API_KEY is not set in this terminal session. "
        "Set it in PowerShell before generating a lesson."
    )

tab_generate, tab_history, tab_about = st.tabs(
    ["✨ Generate lesson", "🧠 Memory & rejection log", "ℹ️ How it works"]
)

with tab_generate:
    left, right = st.columns([1.05, 1.4], gap="large")
    with left:
        st.subheader("Create a lesson")
        with st.form("lesson_form"):
            topic = st.text_input(
                "Lesson topic",
                value="Introduction to RAG",
                help="Enter the topic the learner needs to understand from zero.",
            ).strip()
            simulate_error = st.checkbox(
                "Demo mode: deliberately remove the Example section on attempt 1",
                value=False,
                help="Useful for showing the evaluator detect a failure and request a retry.",
            )
            run_clicked = st.form_submit_button(
                "Generate & evaluate",
                type="primary",
                use_container_width=True,
            )
        st.caption(
            "The app makes up to one initial attempt plus two retries. "
            "Generation requires an available Gemini API quota."
        )

    with right:
        st.subheader("Evaluation dashboard")
        if "last_run" not in st.session_state:
            st.info("Run a lesson to see real rubric results, retry feedback, and the final lesson here.")
        else:
            last = st.session_state["last_run"]
            c1, c2 = st.columns(2)
            c1.metric("Attempts used", f'{last["attempts_used"]} / {1 + MAX_RETRIES}')
            c2.metric("Final status", "PASS" if last["passed"] else "REJECTED")
            for record in last["attempt_records"]:
                with st.expander(
                    f'Attempt {record["attempt"]} — {"PASS" if record["passed"] else "FAIL"}',
                    expanded=(not record["passed"]),
                ):
                    for check, passed in record["checks"].items():
                        a, b = st.columns([3, 1])
                        a.write(check.replace("_", " ").title())
                        b.write("✅ PASS" if passed else "❌ FAIL")
                    if record["failed_checks"]:
                        st.markdown("**Rejection reasons**")
                        for failed in record["failed_checks"]:
                            st.write(f"- {failed.replace('_', ' ').title()}")
                    if record["feedback"]:
                        st.markdown("**Feedback used for this attempt**")
                        for item in record["feedback"]:
                            st.write(f"- {item}")

    if run_clicked:
        if not topic:
            st.error("Please enter a lesson topic.")
        elif not api_ready:
            st.error(
                "Gemini API key is missing. In PowerShell, set it with:\n\n"
                '`$env:GEMINI_API_KEY = Read-Host "Paste your Gemini API key"`\n\n'
                "Then start Streamlit from that same terminal."
            )
        else:
            history = load_memory(topic)
            learning = get_learning_summary(topic)
            feedback = []
            attempt_records = []
            final_lesson = None
            st.session_state.pop("last_error", None)
            status_area = st.status("Starting lesson generation...", expanded=True)
            progress = st.progress(0)

            if history:
                status_area.write(f"Loaded {len(history)} previous attempt record(s) for this topic.")
            if learning.get("recurring_failures"):
                status_area.write("Recurring failures found in memory:")
                for check, count in learning["recurring_failures"]:
                    status_area.write(f"- {check}: failed {count} time(s) previously")

            for attempt in range(1, MAX_RETRIES + 2):
                status_area.write(f"Generating attempt {attempt} of {MAX_RETRIES + 1}...")
                try:
                    lesson = generate_lesson(
                        topic,
                        feedback=feedback or None,
                        simulate_error=(simulate_error and attempt == 1),
                    )
                    result = evaluate_lesson(lesson)
                except Exception as exc:
                    error_message = f"{type(exc).__name__}: {str(exc)}"
                    status_area.update(label="Generation stopped due to an error", state="error")
                    st.error(error_message)
                    st.caption(
                        "This is a generation/API error, not a rubric rejection. "
                        "Check API access, model availability, quota, and the terminal's environment variable."
                    )
                    st.session_state["last_error"] = {
                        "topic": topic,
                        "attempt": attempt,
                        "message": error_message,
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                    }
                    break

                current_feedback = list(feedback)
                save_attempt(topic, attempt, result, current_feedback)
                record = {
                    "attempt": attempt,
                    "passed": result["passed"],
                    "checks": result["checks"],
                    "failed_checks": result["failed_checks"],
                    "feedback": current_feedback,
                }
                attempt_records.append(record)
                for check, passed in result["checks"].items():
                    status_area.write(f'{"✅" if passed else "❌"} {check.replace("_", " ").title()}: {"PASS" if passed else "FAIL"}')

                progress.progress(attempt / (MAX_RETRIES + 1))
                if result["passed"]:
                    final_lesson = lesson
                    status_area.update(label=f"Lesson passed on attempt {attempt}", state="complete")
                    break

                status_area.write("Lesson rejected. Feedback will be sent to the next attempt.")

                # Give the generator actionable feedback for every current failure.
                current_failures = list(result["failed_checks"])
                feedback = [
                    f"The previous lesson failed the '{check}' requirement. Revise it to satisfy this requirement explicitly."
                    for check in current_failures
                ]

                # Emphasize failures seen in saved history.
                recurring_failures = dict(learning.get("recurring_failures", []))
                for check in current_failures:
                    previous_count = recurring_failures.get(check, 0)
                    if previous_count >= 1:
                        feedback.append(
                            f"The '{check}' requirement has failed {previous_count} time(s) in saved history. Check it carefully."
                        )

                if attempt == MAX_RETRIES + 1:
                    status_area.update(label="Retry limit reached; no lesson passed", state="error")

            if attempt_records:
                passed = final_lesson is not None
                output_path = None
                if final_lesson is not None:
                    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                    safe_name = "".join(
                        char.lower() if char.isalnum() else "_"
                        for char in topic
                    ).strip("_")
                    output_path = OUTPUT_DIR / f"{safe_name}_lesson.md"
                    output_path.write_text(final_lesson, encoding="utf-8")
                    st.session_state["last_run"] = {
                        "topic": topic,
                        "passed": passed,
                        "attempts_used": len(attempt_records),
                        "attempt_records": attempt_records,
                        "lesson": final_lesson,
                        "output_path": str(output_path),
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                    }
                    st.success(f"Passing lesson saved to `{output_path.relative_to(PROJECT_DIR)}`.")
                else:
                    st.session_state["last_run"] = {
                        "topic": topic,
                        "passed": False,
                        "attempts_used": len(attempt_records),
                        "attempt_records": attempt_records,
                        "lesson": None,
                        "output_path": None,
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                    }
                    st.error("No passing lesson was produced within the retry limit.")
                st.rerun()

    if st.session_state.get("last_run"):
        last = st.session_state["last_run"]
        st.divider()
        st.subheader("Lesson preview")
        if last.get("lesson"):
            st.markdown(last["lesson"])
            st.download_button(
                "Download lesson as Markdown",
                data=last["lesson"],
                file_name=f"{last['topic'].lower().replace(' ', '_')}_lesson.md",
                mime="text/markdown",
            )
        else:
            st.info("The last run did not produce a passing lesson. Review the evaluation dashboard and rejection log.")

with tab_history:
    st.subheader("Persistent memory")
    try:
        history = load_memory("Introduction to RAG")
        learning = get_learning_summary("Introduction to RAG")
        c1, c2 = st.columns(2)
        c1.metric("Stored attempts for Introduction to RAG", len(history))
        c2.metric("Previously passed attempts", learning.get("previous_passes", 0))
        if learning.get("recurring_failures"):
            st.markdown("**Recurring failures**")
            for check, count in learning["recurring_failures"]:
                st.write(f"- **{check.replace('_', ' ').title()}** — {count} failure(s)")
        else:
            st.info("No recurring failed checks recorded for Introduction to RAG yet.")
    except Exception as exc:
        st.warning(f"Could not read memory: {exc}")

    st.subheader("Rejection log")
    if LOG_FILE.exists():
        try:
            log_data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            if log_data:
                st.dataframe(log_data, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download rejection log JSON",
                    data=json.dumps(log_data, indent=2, ensure_ascii=False),
                    file_name="rejection_log.json",
                    mime="application/json",
                )
            else:
                st.info("Rejection log is currently empty.")
        except (json.JSONDecodeError, OSError) as exc:
            st.error(f"Could not read rejection log: {exc}")
    else:
        st.info("No rejection log exists yet. Run a lesson to create it.")

with tab_about:
    st.subheader("Workflow overview")
    st.markdown(
        """
        1. **Generate:** Gemini creates a standalone lesson.
        2. **Evaluate:** The local Python rubric returns PASS/FAIL for each check.
        3. **Reject and explain:** Failed checks become explicit feedback.
        4. **Retry:** The generator gets feedback, up to the configured retry limit.
        5. **Persist:** Each evaluation is stored in the JSON rejection log.
        6. **Learn from history:** Repeated failures can add extra emphasis to retry feedback.

        **Current limitation:** the evaluator is mostly text-pattern based. A PASS does not independently prove every fact is correct, and this app does not retrieve external source documents to verify citations.
        """
    )
    st.code("python -m unittest test_workflow -v", language="powershell")
    st.caption("The automated tests use local sample content and mocks; they do not call Gemini.")
