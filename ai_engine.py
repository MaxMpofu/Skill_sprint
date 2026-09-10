"""
The AI Challenge Engine.

If OPENAI_API_KEY is set, generates a fresh trend-aware brief with an LLM.
Otherwise falls back to a rotating pool of canned briefs so the app is
fully runnable with zero API keys configured (good for a hackathon demo).
"""

import os
import json
import random

FALLBACK_BRIEFS = [
    {
        "title": "Build a simple HTTP web server",
        "description": "Stand up a minimal HTTP server that handles at least GET and POST requests.",
        "twist": "Your creative twist could add rate-limiting, a live analytics dashboard, or a chat relay.",
        "source": "GitHub Trending: lightweight server frameworks",
    },
    {
        "title": "Build a URL shortener",
        "description": "Take a long URL and return a short, unique redirect link.",
        "twist": "Add click analytics, expiring links, or a custom QR-code generator.",
        "source": "Dev blogs: API design patterns",
    },
    {
        "title": "Build a command-line task tracker",
        "description": "A CLI tool to add, complete, and list tasks, persisted to disk.",
        "twist": "Add natural-language due dates, a Kanban view, or a Slack-style bot interface.",
        "source": "Job-market signal: CLI tooling demand up",
    },
    {
        "title": "Build a real-time polling app",
        "description": "Let users create a poll and watch votes update live for anyone with the link.",
        "twist": "Add anonymous vs. verified voting, live result charts, or a countdown-timed poll.",
        "source": "Trend source: real-time web frameworks",
    },
]


def _generate_with_openai(recent_titles):
    from openai import OpenAI  # imported lazily so the package is optional

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"""You are the AI Challenge Engine for SkillSprint, a platform that gives
student developers a new coding brief every week.

Avoid repeating these recent briefs: {', '.join(recent_titles) or 'none yet'}.

Return ONLY valid JSON with these exact keys: title, description, twist, source.
- title: a short project name (max 8 words)
- description: one sentence describing the core build
- twist: one sentence suggesting 2-3 optional creative directions
- source: a short label naming the kind of trend signal that inspired this (e.g. "GitHub Trending: ...")
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def generate_weekly_brief(recent_titles=None):
    """
    Returns a dict: {title, description, twist, source}.
    Uses OpenAI if OPENAI_API_KEY is set in the environment, else a local
    rotating pool (never repeats the same brief twice in a row).
    """
    recent_titles = recent_titles or []

    if os.environ.get("OPENAI_API_KEY"):
        try:
            return _generate_with_openai(recent_titles)
        except Exception:
            pass  # fall through to offline pool on any API error

    candidates = [b for b in FALLBACK_BRIEFS if b["title"] not in recent_titles] or FALLBACK_BRIEFS
    return random.choice(candidates)
