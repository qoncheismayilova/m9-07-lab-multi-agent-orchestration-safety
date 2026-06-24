import json
import ollama


# -----------------------------------
# GET AVAILABLE MODEL
# -----------------------------------
def get_available_model():
    models_response = ollama.list()

    models = models_response.models

    if not models:
        raise Exception(
            "No model found. Run: ollama pull llama3"
        )

    model_names = [model.model for model in models]

    for preferred in ["llama3", "mistral", "phi3"]:
        for model in model_names:
            if preferred in model.lower():
                return model

    return model_names[0]


MODEL_NAME = get_available_model()

print(f"Using model: {MODEL_NAME}")


# -----------------------------------
# LOAD NOTES
# -----------------------------------
with open("notes.json", "r", encoding="utf-8") as f:
    notes = json.load(f)


# -----------------------------------
# SUMMARY AGENT
# -----------------------------------
def summary_agent(notes_text):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Summarize these business notes into one paragraph."
            },
            {
                "role": "user",
                "content": notes_text
            }
        ]
    )

    return response.message.content


# -----------------------------------
# HEADLINE AGENT
# -----------------------------------
def headline_agent(summary_text):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Create one short business headline from this summary."
            },
            {
                "role": "user",
                "content": summary_text
            }
        ]
    )

    return response.message.content


# -----------------------------------
# GUARDRAIL
# -----------------------------------
def sanitize_notes(notes):
    clean_notes = []

    suspicious_patterns = [
        "ignore all previous instructions",
        "forget previous instructions",
        "system override"
    ]

    for note in notes:
        text = note["text"].lower()

        blocked = False

        for pattern in suspicious_patterns:
            if pattern in text:
                print(f"⚠ Injection detected in {note['id']}")
                blocked = True
                break

        if not blocked:
            clean_notes.append(note)

    return clean_notes


# -----------------------------------
# BEFORE DEFENSE
# -----------------------------------
print("\n===== BEFORE DEFENSE =====")

raw_notes = "\n".join(
    note["text"] for note in notes
)

summary = summary_agent(raw_notes)
headline = headline_agent(summary)

print("\nSummary:")
print(summary)

print("\nHeadline:")
print(headline)


# -----------------------------------
# AFTER DEFENSE
# -----------------------------------
print("\n===== AFTER DEFENSE =====")

safe_notes = sanitize_notes(notes)

safe_input = "\n".join(
    note["text"] for note in safe_notes
)

safe_summary = summary_agent(safe_input)
safe_headline = headline_agent(safe_summary)

print("\nSummary:")
print(safe_summary)

print("\nHeadline:")
print(safe_headline)