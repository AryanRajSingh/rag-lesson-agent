
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "outputs"
LOG_FILE = OUTPUT_DIR / "rejection_log.json"


def read_history():
    """Read saved history without deleting existing records."""

    if not LOG_FILE.exists():
        return []

    try:
        history = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        return history if isinstance(history, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_attempt(topic, attempt, result, feedback=None):
    """Save one evaluation attempt to persistent JSON memory."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    history = read_history()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "attempt": attempt,
        "passed": result["passed"],
        "checks": result["checks"],
        "failed_checks": result["failed_checks"],
        "feedback": feedback or [],
    }

    history.append(record)

    LOG_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_memory(topic):
    """Load previous attempts for the requested topic."""

    return [
        record
        for record in read_history()
        if record.get("topic", "").strip().lower()
        == topic.strip().lower()
    ]


def get_learning_summary(topic):
    """Summarize recurring failures from previous attempts."""

    history = load_memory(topic)

    failures = Counter(
        check
        for record in history
        for check in record.get("failed_checks", [])
    )

    return {
        "previous_attempts": len(history),
        "previous_passes": sum(
            1 for record in history if record.get("passed") is True
        ),
        "recurring_failures": failures.most_common(),
    }
