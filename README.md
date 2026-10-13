
# Self-Evaluating Lesson Generator

A Python-based content generation pipeline that creates a beginner-friendly lesson, evaluates it against explicit pass/fail criteria, and retries when requirements are not met.

The project uses the Gemini API for lesson generation and a local Python evaluator for automated checks. Attempt history and recurring failure patterns are stored in JSON.

## Features

- Generate a standalone lesson about Introduction to RAG.
- Evaluate lesson structure and required concepts using a pass/fail rubric.
- Return failure reasons when a lesson does not pass.
- Regenerate failed lessons using evaluator feedback.
- Limit generation to one initial attempt and two retries.
- Persist attempt history in a JSON rejection log.
- Summarize recurring failures to guide future retry prompts.
- Run automated tests without making API calls.

## Architecture

1. **Generator:** Requests lesson content from Gemini.
2. **Evaluator:** Checks the definition, importance, workflow, example, terminology, key concepts, limitations, and beginner-friendly structure.
3. **Controller:** Accepts a passing lesson or retries with feedback.
4. **Memory:** Stores evaluation results, feedback, and timestamps in JSON.
5. **Outputs:** Saves the generated lesson as a Markdown file and keeps the attempt history.
6. **Tests:** Verify evaluation and retry behaviour using offline sample content and mocks.

## Requirements

- Python 3.10 or newer (Python 3.13 has been used for development).
- Git.
- A Gemini API key available through Google's AI Studio.
- Internet access when generating a lesson with Gemini.

The project uses the `google-genai` Python SDK. No local language model, GPU, or Docker is required.

## Setup

Open PowerShell in the project directory.

Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configure the API key

Obtain an API key from Google AI Studio and configure it in your current PowerShell session:

```powershell
$env:GEMINI_API_KEY = Read-Host "Paste your Gemini API key"
```

Paste the key when prompted. Do not put the key in source code, commit it to Git, or share it in a recording.

API availability, model access, rate limits, and free-tier quotas depend on Google's current policies and account eligibility. This project does not require enabling paid billing, but API access is not guaranteed to remain free or available at all times.

## Run the workflow

```powershell
python main.py
```

Enter a topic when prompted. For the required demonstration, use:

`Introduction to RAG`

When asked whether to simulate a missing-example error, enter `y` to test whether the evaluator detects the missing example and whether the retry process can correct it. Enter `n` for a normal generation run.

The workflow permits a maximum of three attempts: one initial attempt plus two retries.

## Outputs

- `outputs/introduction_to_rag_lesson.md` — saved lesson for the RAG topic.
- `outputs/rejection_log.json` — attempt history, check results, failure reasons, feedback, and timestamps.

The rejection log is persistent across runs. Existing test or demonstration records may also appear in it.

## Run tests

```powershell
python -m unittest test_workflow -v
```

The automated tests use sample content and mocked generator calls, so they do not need a Gemini API key or consume API quota.

## Evaluation rubric

The evaluator checks:

- Definition and introduction.
- Importance and practical value.
- Numbered workflow steps.
- A practical example.
- Explanation of retrieval and generation.
- Required concepts, including documents and model.
- Limitations and answer correctness.
- Beginner-friendly length and structure.
- Non-empty lesson content.

A lesson passes only when every implemented check passes.

## Memory and self-improvement

The workflow stores evaluation history in a local JSON file. It can summarize recurring failed checks and include relevant failure patterns in subsequent generation feedback.

This is a lightweight, rule-based memory mechanism. It does not automatically retrain the model or rewrite the evaluator's rubric.

## Limitations

- Most evaluator checks are based on text patterns and structure.
- A passing result does not prove that every factual claim is correct.
- The system does not currently provide independent source retrieval or citation verification.
- Memory uses local JSON and is not shared across machines.
- API access depends on the configured Gemini model and current service limits.

## Repository hygiene

Keep `.env`, API keys, `.venv`, and Python cache files out of version control. Never commit credentials or include them in screenshots or demo recordings.
