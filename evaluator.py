
import re


def evaluate_lesson(lesson):
    """Check essential content in a beginner-friendly lesson."""

    text = lesson.lower()
    words = re.findall(r"\b[\w'-]+\b", text)

    headings = [
        line.strip().lstrip("#").strip().lower()
        for line in lesson.splitlines()
        if line.strip().startswith("#")
    ]

    def has_heading(*terms):
        return any(
            term in heading
            for heading in headings
            for term in terms
        )

    def contains_any(*phrases):
        return any(phrase in text for phrase in phrases)

    # 1. Topic definition and explanation of retrieval.
    definition = (
        contains_any(
            "retrieval-augmented generation",
            "rag stands for",
        )
        and contains_any(
            "looks up relevant facts",
            "looks up relevant information",
            "searches a database",
            "searches through documents",
            "retrieves relevant information",
            "find relevant information",
            "find the ones that match",
            "external collection of texts",
            "search specific documents",
            "searches relevant documents",
        )
    )

    # 2. Why RAG is useful.
    importance = (
        has_heading("why", "importance", "benefit")
        and contains_any(
            "outdated information",
            "up-to-date",
            "up to date",
            "news that happened yesterday",
            "private information",
            "guess the answer",
            "might guess",
            "make up a convincing falsehood",
            "make things up",
            "incorrect answers",
            "more accurate",
            "trusted information",
        )
    )

    # 3. A process with ordered steps.
    numbered_steps = sum(
        bool(re.match(r"^\s*\d+[\s:.)-]", line))
        for line in lesson.splitlines()
    )

    working_steps = (
        numbered_steps >= 3
        and contains_any("search", "retrieval", "retrieve")
        and contains_any("generate", "generation", "writes a final answer")
    )

    # 4. A practical example with a question and result.
    practical_example = (
        has_heading("example", "scenario", "walkthrough")
        and contains_any(
            "realistic question",
            "for example",
            "imagine",
            "suppose",
        )
        and contains_any(
            "resulting answer",
            "the answer is",
            "asks",
            "question",
        )
    )

    # 5. Technical terms explained in simple language.

    retrieval_explained = (
        contains_any(
            "retrieval means",
            "retrieval is the process",
            "retrieval: the system searches",
            "retrieval. the system searches",
            "librarian performing retrieval",
            "retrieval step searches",
            "retrieval is searching",
            "retrieval refers to searching",
            "retrieval means searching",
        )
        or (
            "retrieval" in text
            and contains_any(
                "searches a database",
                "searches through documents",
                "find the ones that match",
                "find the exact pages",
                "looks up relevant facts",
                "searches for relevant documents",
                "find relevant information",
                "searching a database",
                "searching through documents",
                "find the relevant documents",
                "searches stored files",
                "scans through stored files",
            )
        )
    )




    generation_explained = (
        contains_any(
            "generation means",
            "generation is the process",
            "generation step happens",
            "generation step",
            "generation: the ai",
            "generation. the ai",
            "text-writing part",
            "writes a final answer",
            "writes an answer",
            "text-writing",
            "writes a clear, helpful response",
            "reads the retrieved pages",
            "summarizes or explains the information",
            "final answer",
            "ai reads the combined text",
            "writes the answer",
            "writes an answer based on",
        )
        or (
            "generation" in text
            and contains_any(
                "writes",
                "creates",
                "produces",
                "generates",
                "summarizes",
            )
            and contains_any("answer", "response", "text")
        )
    )



    jargon_explained = (
        retrieval_explained and generation_explained
    )

    # 6. Essential concepts are present.
    key_concepts = all(
        contains_any(term)
        for term in [
            "retrieval",
            "document",
            "model",
            "generation",
        ]
    )

    # 7. At least one genuine limitation is described.
    limitations_explained = (
        has_heading("limitation", "what rag cannot do")
        and contains_any(
            "does not guarantee",
            "doesn't guarantee",
            "cannot guarantee",
            "not always correct",
            "not always accurate",
            "wrong answer",
            "wrong answers",
            "errors",
            "mistakes",
        )
    )

    # 8. Sufficient length and a concluding section.
    beginner_friendly = (
        150 <= len(words) <= 1200
        and has_heading("summary", "key takeaway", "conclusion")
    )

    checks = {
        "definition": definition,
        "importance": importance,
        "working_steps": working_steps,
        "practical_example": practical_example,
        "jargon_explained": jargon_explained,
        "key_concepts": key_concepts,
        "limitations_explained": limitations_explained,
        "beginner_friendly": beginner_friendly,
        "no_empty_lesson": len(words) > 0,
    }

    failed_checks = [
        name for name, passed in checks.items() if not passed
    ]

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "failed_checks": failed_checks,
    }
