
from generator import generate_lesson
from evaluator import evaluate_lesson
from memory import save_attempt, load_memory, get_learning_summary
from config import MAX_RETRIES


from pathlib import Path


def save_final_lesson(topic, lesson):
    """Save the accepted lesson as a Markdown file."""

    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(
        char.lower() if char.isalnum() else "_"
        for char in topic
    ).strip("_")

    file_path = output_dir / f"{safe_name}_lesson.md"
    file_path.write_text(lesson, encoding="utf-8")

    print(f"Final lesson saved to: {file_path}")

def run_workflow(topic, simulate_error=False):
    """Generate, evaluate and retry a lesson with a fixed limit."""

    previous_runs = load_memory(topic)
    learning = get_learning_summary(topic)

    if learning["recurring_failures"]:
        print("\nMemory learning summary:")

        for check, count in learning["recurring_failures"]:
            print(f"- {check} failed {count} time(s) previously")
    previous_failures = [
        check
        for record in previous_runs
        for check in record.get("failed_checks", [])
    ]

    if previous_runs:
        print(f"Memory loaded: {len(previous_runs)} previous attempts.")

    if previous_failures:
        print("Previously failed checks:", ", ".join(previous_failures))

    feedback = []
    final_lesson = None
    attempts_used = 0

    for attempt in range(MAX_RETRIES + 1):
        attempts_used += 1
        print(f"\n--- ATTEMPT {attempt + 1} ---")

        lesson = generate_lesson(
            topic,
            feedback=feedback or None,
            simulate_error=simulate_error,
        )
        result = evaluate_lesson(lesson)
        save_attempt(topic, attempt + 1, result, feedback)

        for check, passed in result["checks"].items():
            print(f"{check}: {'PASS' if passed else 'FAIL'}")

        if result["passed"]:
            final_lesson = lesson
            print("\nLesson passed all evaluation checks.")
            break

        feedback = [
            f"Please fix the failed requirement: {check}"
            for check in result["failed_checks"]
        ]

        # Use past failure patterns to strengthen retry guidance.
        for check, count in learning["recurring_failures"]:
            if check in result["failed_checks"] and count >= 1:
                feedback.append(
                    f"This requirement has failed before. "
                    f"Pay extra attention to: {check}"
                )

        print("\nLesson rejected.")
        print("Reasons:", ", ".join(result["failed_checks"]))

        if attempt < MAX_RETRIES:
            print("Retrying with feedback...")
        else:
            print("Retry limit reached. Lesson was not accepted.")

    return final_lesson, attempts_used


def main():
    topic = input("Enter the lesson topic: ").strip()

    if not topic:
        print("Topic cannot be empty.")
        return

    choice = input(
        "Simulate a missing-example error? (y/n): "
    ).strip().lower()

    lesson, attempts = run_workflow(
        topic,
        simulate_error=(choice == "y"),
    )

    if lesson is not None:
        print("\n--- FINAL LESSON ---")
        print(lesson)
        save_final_lesson(topic, lesson)
    else:
        print("\nNo passing lesson was produced.")

    print(f"\nAttempts used: {attempts}")
    print("Rejection log: outputs/rejection_log.json")


if __name__ == "__main__":
    main()
