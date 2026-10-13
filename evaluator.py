
def evaluate_lesson(lesson):
    """Check lesson structure and essential beginner-learning requirements."""

    text = lesson.lower()
    words = text.split()

    checks = {
        "definition": (
            "retrieval-augmented generation" in text
            and "find relevant" in text
        ),

        "importance": (
            "why does rag matter?" in text
            and "documents" in text
            and "latest information" in text
        ),

        "working_steps": all(
            step in text
            for step in [
                "step 1:",
                "step 2:",
                "step 3:",
                "step 4:",
            ]
        ),

        "practical_example": (
            "## 4. example" in text
            and "student" in text
            and "college" in text
            and "asks" in text
        ),

        "jargon_explained": (
            "retrieval means" in text
            and "generation means" in text
            and "document is a source" in text
        ),

        "key_concepts": all(
            term in text
            for term in [
                "retrieval",
                "documents",
                "generate an answer",
                "model",
            ]
        ),

        "limitations_explained": (
            "quality depends on" in text
            and "retrieved" in text
        ),

        "beginner_friendly": (
            "## 6. summary" in text
            and len(words) >= 150
            and len(words) <= 1000
        ),

        "no_empty_lesson": len(words) > 0,
    }

    failed_checks = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "failed_checks": failed_checks,
    }
