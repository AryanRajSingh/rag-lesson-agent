
def generate_lesson(topic, feedback=None, simulate_error=False):
    """Create an offline lesson for workflow testing."""

    lesson = f"""# {topic}

## 1. What is RAG?

RAG stands for Retrieval-Augmented Generation.
It helps an AI system find relevant information from
documents before generating an answer.

## 2. Why does RAG matter?

An AI model may not know the latest information
or private information stored in your documents.
RAG provides relevant information to help the model
answer questions using those documents.

## 3. How does RAG work?

Step 1: A user asks a question.
Step 2: The system searches relevant documents.
Step 3: It retrieves useful information from those documents.
Step 4: The AI model uses that information to generate an answer.

## 4. Example

Imagine a college has hundreds of pages of student rules.
A student asks, "What is the attendance requirement?"

A RAG system searches the college documents, retrieves
the relevant attendance rule, and uses it to help
generate an answer.

## 5. Important terms

Retrieval means finding relevant information.
Generation means creating a response.
A document is a source of information, such as a text file.

## 6. Summary

RAG combines information retrieval with AI text generation.
It can help answers use relevant documents, but answer
quality depends on the documents retrieved and how
the model uses that information.
"""

    # Testing only: deliberately remove the example.
    if simulate_error and not feedback:
        start = lesson.find("## 4. Example")
        end = lesson.find("## 5. Important terms")

        if start != -1 and end != -1:
            lesson = lesson[:start] + lesson[end:]

    # Restore the example if the evaluator reports a failure.
    if feedback:
        feedback_text = " ".join(feedback).lower()

        needs_example = (
            "practical_example" in feedback_text
            or "practical example" in feedback_text
        )

        example_missing = (
            "## 4. example" not in lesson.lower()
            or "student" not in lesson.lower()
            or "college" not in lesson.lower()
            or "asks" not in lesson.lower()
        )

        if needs_example and example_missing:
            example_section = """## 4. Example

Imagine a college stores its student rules in documents.
A student asks, "What is the attendance requirement?"

The RAG system searches the college documents and retrieves
the relevant attendance rule. The AI model uses that
information to help generate an answer.

This example shows how a question is connected to relevant
documents before the answer is generated.
"""
            marker = "## 5. Important terms"

            if marker in lesson:
                lesson = lesson.replace(
                    marker,
                    example_section + "\n" + marker,
                    1,
                )
            else:
                lesson += "\n" + example_section

    return lesson
