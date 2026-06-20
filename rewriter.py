"""
rewriter.py
-----------
Uses the Claude API to rewrite weak resume bullet points so they
naturally incorporate the missing keywords and read as stronger,
quantified achievements - without fabricating experience the
candidate doesn't have.
"""

import os
import json
from anthropic import Anthropic

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

_MODEL = "claude-sonnet-4-6"

_SYSTEM_PROMPT = """You are a professional resume writer. You will be given:
1. A list of existing resume bullet points
2. A list of keywords missing from the resume that are relevant to a target job

Rewrite each bullet point to be stronger and more quantified (use metrics
where plausible), and naturally weave in missing keywords ONLY where they
genuinely fit the described work. Do NOT invent skills, tools, or
achievements that aren't implied by the original bullet.

Return ONLY valid JSON in this exact format, with no extra commentary:
{"rewrites": [{"original": "...", "improved": "..."}]}
"""


def rewrite_bullets(bullets: list[str], missing_keywords: list[str]) -> list[dict]:
    """
    Sends the resume bullets + missing keywords to Claude and returns
    a list of {"original": ..., "improved": ...} dicts.
    """
    if not bullets:
        return []

    user_message = (
        f"Resume bullet points:\n"
        + "\n".join(f"- {b}" for b in bullets)
        + f"\n\nMissing keywords from the target job:\n"
        + ", ".join(missing_keywords)
    )

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=1500,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(raw_text)
        return parsed.get("rewrites", [])
    except json.JSONDecodeError:
        # If the model didn't return clean JSON, fail gracefully.
        return [{"original": b, "improved": "(rewrite failed - see raw response)"} for b in bullets]


if __name__ == "__main__":
    sample_bullets = [
        "Worked on improving backend performance.",
        "Helped manage a small team of developers.",
    ]
    sample_missing = ["Python", "AWS", "team leadership", "CI/CD"]

    if os.environ.get("ANTHROPIC_API_KEY"):
        for item in rewrite_bullets(sample_bullets, sample_missing):
            print("-", item["original"])
            print("  ->", item["improved"])
    else:
        print("Set ANTHROPIC_API_KEY to test the rewriter live.")