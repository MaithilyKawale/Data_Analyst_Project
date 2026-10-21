"""Optional OpenAI-powered narrative insights with a local fallback."""
import os
from src.analytics import deterministic_insights

def generate_insights(df):
    facts = deterministic_insights(df)
    if not os.getenv("OPENAI_API_KEY"):
        return facts, "Local mode (no API key configured)."
    try:
        from openai import OpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = OpenAI().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a cautious business analyst. Use only supplied facts, invent no numbers, do not claim causation, and state limitations."},
                {"role": "user", "content": "Write 3 concise insights and 2 caveats from these computed facts:\n" + "\n".join(facts)},
            ],
            temperature=0.2,
        )
        narrative = response.choices[0].message.content or "\n".join(facts)
        return narrative.splitlines(), f"AI-assisted mode ({model}); verify statements before sharing."
    except Exception as exc:
        return facts, f"Local fallback used because the AI request failed ({type(exc).__name__})."
