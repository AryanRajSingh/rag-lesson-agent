
import os
from google import genai

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_lesson(topic, feedback=None, simulate_error=False):
    """Generate a beginner-friendly lesson using Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Set it in your terminal before running the workflow."
        )

    client = genai.Client(
        api_key=api_key,
        http_options={"timeout": 60000},
    )

    feedback_text = ""
    if feedback:
        feedback_text = (
            "\n\nEvaluator feedback from the previous attempt:\n- "
            + "\n- ".join(feedback)
            + "\nFix every listed issue. Keep content that already "
            "satisfies the requirements."
        )

    prompt = f"""
You are a patient teacher writing a standalone beginner lesson.

Topic: {topic}

Assume the learner is starting from zero.
Write approximately 400-700 words in simple English.

MANDATORY REQUIREMENTS:

1. Define the topic clearly in simple English.
2. For RAG, include the exact phrase
   "Retrieval-Augmented Generation".
3. Explain why the topic matters and when it is useful.
4. Explain the workflow in 3-5 numbered steps.
5. For RAG, explain how a question leads to document retrieval
   and then to answer generation.
6. Include a heading containing the word "Example".
7. In the example, show a realistic question, relevant
   document information, and the resulting answer.
8. Explain at least two technical terms in simple language.
9. Include the concepts retrieval, documents, model,
   and generation in meaningful sentences.
10. Explain at least one limitation honestly.
11. For RAG, explain that retrieving documents does not
    guarantee that every generated answer is correct.
12. Finish with a heading containing the word "Summary".
13. Use clear Markdown headings, lists, and paragraphs.
14. Use proper spaces between words and sentences.
15. Avoid unexplained jargon and unsupported factual claims.
16. Do not invent sources or pretend to have searched
    documents that were not provided.
17. Return only the lesson, without commentary about
    these instructions.

Before returning the lesson, check that all requirements
are covered and that the writing is readable.

{feedback_text}
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    lesson = (interaction.output_text or "").strip()

    if not lesson:
        raise RuntimeError("Gemini returned an empty lesson.")

    # Demo-only: deliberately remove the Example section
    # so the evaluator can detect a missing requirement.
    if simulate_error and not feedback:
        lines = lesson.splitlines()
        filtered = []
        skipping = False

        for line in lines:
            is_heading = line.strip().startswith("#")

            if is_heading and "example" in line.lower():
                skipping = True
                continue

            if skipping and is_heading:
                skipping = False

            if not skipping:
                filtered.append(line)

        lesson = "\n".join(filtered)

    return lesson
