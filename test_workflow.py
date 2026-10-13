
import unittest
from unittest.mock import patch

from main import run_workflow
from evaluator import evaluate_lesson


SAMPLE_LESSON = """
# Introduction to RAG

## What Is RAG?

RAG stands for Retrieval-Augmented Generation. It helps an AI model
look up relevant information in documents before writing an answer.

## Why Does RAG Matter?

Without relevant information, an AI might make things up or give
incorrect answers. RAG helps it use trusted information for questions
about company policies, manuals, and other stored documents.

## How RAG Works

1. The user asks a question.
2. Retrieval searches a database for relevant documents.
3. The system combines the question with the retrieved information.
4. Generation uses the information to write a final answer.

## Technical Terms

- **Retrieval:** Retrieval means searching through documents to find
  relevant information.
- **Generation:** Generation means the AI writes an answer or response
  using the information it receives.
- **Model:** A model is a computer program trained to process language.
- **Documents:** Documents are files, articles, or notes that can be searched.

## Example of RAG

Imagine a customer asks, "What is the return policy for opened items?"

Relevant document information says customers may return opened items
within 14 days if they have the original receipt.

The resulting answer is: "You can return opened items within 14 days
if you have your original receipt."

## Limitations

Retrieving documents does not guarantee that every generated answer
is correct. The documents may contain errors, or the AI may misunderstand
the information and produce a wrong answer.

## Summary

RAG combines document retrieval with answer generation. It can help an
AI answer questions using relevant information, but its answers still
need to be checked.
"""


class TestLessonWorkflow(unittest.TestCase):

    def test_normal_lesson_passes(self):
        result = evaluate_lesson(SAMPLE_LESSON)

        self.assertTrue(result["passed"], result["failed_checks"])
        self.assertEqual(result["failed_checks"], [])

    def test_missing_example_is_rejected(self):
        # Remove the example section without relying on exact heading numbers.
        start = SAMPLE_LESSON.lower().find("## example")
        end = SAMPLE_LESSON.lower().find("## limitations")

        self.assertNotEqual(start, -1)
        self.assertNotEqual(end, -1)

        broken_lesson = SAMPLE_LESSON[:start] + SAMPLE_LESSON[end:]
        result = evaluate_lesson(broken_lesson)

        self.assertFalse(result["passed"])
        self.assertIn("practical_example", result["failed_checks"])

    @patch("main.save_attempt")
    @patch("main.load_memory", return_value=[])
    @patch("main.get_learning_summary", return_value={
        "previous_attempts": 0,
        "previous_passes": 0,
        "recurring_failures": [],
    })
    @patch("main.generate_lesson")
    def test_retry_limit_stops_after_two_retries(
        self,
        mock_generator,
        mock_learning,
        mock_memory,
        mock_save,
    ):
        start = SAMPLE_LESSON.lower().find("## example")
        end = SAMPLE_LESSON.lower().find("## limitations")
        broken_lesson = SAMPLE_LESSON[:start] + SAMPLE_LESSON[end:]

        mock_generator.return_value = broken_lesson

        result, attempts = run_workflow("Retry limit test")

        self.assertIsNone(result)
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_generator.call_count, 3)

    @patch("main.generate_lesson")
    def test_feedback_restores_missing_example(self, mock_generator):
        start = SAMPLE_LESSON.lower().find("## example")
        end = SAMPLE_LESSON.lower().find("## limitations")
        broken_lesson = SAMPLE_LESSON[:start] + SAMPLE_LESSON[end:]

        # First attempt fails; second attempt returns a corrected lesson.
        mock_generator.side_effect = [broken_lesson, SAMPLE_LESSON]

        first_result = evaluate_lesson(mock_generator("Introduction to RAG"))
        self.assertFalse(first_result["passed"])
        self.assertIn("practical_example", first_result["failed_checks"])

        feedback = [
            f"Please fix the failed requirement: {check}"
            for check in first_result["failed_checks"]
        ]

        corrected_lesson = mock_generator(
            "Introduction to RAG",
            feedback=feedback,
        )
        second_result = evaluate_lesson(corrected_lesson)

        self.assertTrue(second_result["passed"], second_result["failed_checks"])
        self.assertEqual(second_result["failed_checks"], [])

    def test_empty_lesson_is_rejected(self):
        result = evaluate_lesson("")

        self.assertFalse(result["passed"])
        self.assertTrue(result["failed_checks"])


if __name__ == "__main__":
    unittest.main()
