
import os
import sys
from google import genai


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: GEMINI_API_KEY is not configured.")
        sys.exit(1)

    try:
        client = genai.Client(
            api_key=api_key,
            http_options={"timeout": 60000},
        )

        print("Connecting to Gemini...")

        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input="Explain RAG in one simple sentence.",
        )

        answer = interaction.output_text

        if answer:
            print("\nGemini API connection successful!")
            print("Response:", answer)
        else:
            print("No text returned by the model.")

    except Exception as error:
        print("\nGemini API request failed.")
        print("Error type:", type(error).__name__)
        print("Details:", str(error)[:400])
        sys.exit(1)


if __name__ == "__main__":
    main()
