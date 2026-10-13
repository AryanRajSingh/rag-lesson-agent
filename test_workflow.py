
import unittest
from unittest.mock import patch

from main import run_workflow
from generator import generate_lesson
from evaluator import evaluate_lesson


class TestLessonWorkflow(unittest.TestCase):

    def test_feedback_restores_missing_example(self):
        # Deliberately remove the example.
        broken_lesson = generate_lesson(
            "Introduction to RAG",
            simulate_error=True,
        )

        first_result = evaluate_lesson(broken_lesson)

        self.assertFalse(first_result["passed"])
        self.assertIn(
            "practical_example",
            first_result["failed_checks"],
        )

        # Send the failure reason back as feedback.
        feedback = [
            f"Please fix the failed requirement: {check}"
            for check in first_result["failed_checks"]
        ]

        corrected_lesson = generate_lesson(
            "Introduction to RAG",
            feedback=feedback,
        )

        second_result = evaluate_lesson(corrected_lesson)

        self.assertTrue(second_result["passed"])
        self.assertEqual(second_result["failed_checks"], [])

    @patch("main.generate_lesson")
    def test_retry_limit_stops_after_two_retries(self, mock_generator):
        # Always return a lesson with its example removed.
        lesson = generate_lesson("Introduction to RAG")
        start = lesson.find("## 4. Example")
        end = lesson.find("## 5. Important terms")

        broken_lesson = lesson[:start] + lesson[end:]
        mock_generator.return_value = broken_lesson

        result, attempts = run_workflow("Retry limit test")

        self.assertIsNone(result)
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_generator.call_count, 3)

    def test_normal_lesson_passes(self):
        lesson = generate_lesson("Introduction to RAG")
        result = evaluate_lesson(lesson)

        self.assertTrue(result["passed"])
        self.assertEqual(result["failed_checks"], [])

    def test_missing_example_is_rejected(self):
        lesson = generate_lesson("Introduction to RAG")

        start = lesson.find("## 4. Example")
        end = lesson.find("## 5. Important terms")

        self.assertNotEqual(start, -1)
        self.assertNotEqual(end, -1)

        lesson = lesson[:start] + lesson[end:]
        result = evaluate_lesson(lesson)

        self.assertFalse(result["passed"])
        self.assertIn(
            "practical_example",
            result["failed_checks"],
        )

    def test_empty_lesson_is_rejected(self):
        result = evaluate_lesson("")

        self.assertFalse(result["passed"])
        self.assertTrue(result["failed_checks"])


if __name__ == "__main__":
    unittest.main()
