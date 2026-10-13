
# Self-Evaluating Lesson Content Generator

A beginner-friendly Python project that demonstrates a
generate, evaluate, and regenerate workflow for lesson content.

## 1. Project Goal

The goal is to create a system that generates a lesson on
Introduction to RAG, evaluates it using pass/fail criteria,
and retries when mandatory checks fail.

## 2. Current Implementation

This project currently uses an offline lesson template.
It does not yet use a real AI model or API.

The offline version helps test the workflow without API
charges or heavy model downloads.

## 3. Architecture

1. Topic input: accepts a lesson topic.
2. Generator: creates a lesson using the offline template.
3. Evaluator: checks required concepts and lesson structure.
4. Controller: accepts passing lessons or retries failed ones.
5. Memory: stores attempt history in JSON.
6. Tests: verify normal, invalid, and retry-limit cases.

## 4. Evaluation Criteria

The evaluator checks:

- Definition and introduction
- Importance of the topic
- Working steps
- Practical example
- Explanation of key terms
- Required concepts
- Beginner-friendly structure

Each criterion returns PASS or FAIL.

## 5. Retry Behaviour

The workflow allows one initial attempt and up to two retries.
If all attempts fail, the lesson is rejected.

Failure reasons are saved in the rejection log.

## 6. Requirements

- Python 3.13 or a compatible Python version
- Visual Studio Code (recommended)
- Git for version control

No external Python packages are currently required.

## 7. Setup

Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

Run the program:

```powershell
python main.py
```

Run automated tests:

```powershell
python -m unittest test_workflow -v
```

## 8. Output and Logs

Evaluation history is stored in:

`outputs/rejection_log.json`

The log contains timestamps, topics, attempt numbers,
check results, failure reasons, and feedback.

## 9. Testing

The current test suite covers:

- Normal lesson acceptance
- Missing-example rejection
- Empty lesson rejection
- Feedback-based example correction
- Retry-limit enforcement

## 10. Current Limitations

- Lesson generation uses a fixed offline template.
- Evaluation is mainly based on text and structure checks.
- The current version does not independently verify all facts.
- Memory stores history, but long-term self-improvement
  is not yet fully implemented.
- A real AI model integration remains future work.

## 11. Planned Improvements

- Integrate a suitable free-access AI model API.
- Add stronger factual accuracy and grounding checks.
- Use repeated failure patterns to improve future instructions.
- Save the final accepted lesson separately.
- Add end-to-end tests and a demonstration workflow.
