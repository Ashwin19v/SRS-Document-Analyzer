import json
import os
from typing import Dict, List
import httpx
from ..settings import settings

SYSTEM_PROMPT = (
    "You are a senior software architect. Given an SRS, suggest a concise modern tech stack "
    "(frontend, backend, DB, infra, GenAI). Return ONLY a JSON object with 'tech_stack': string[]."
)

DEFAULT_TECH_STACK = [
    "React + Vite + TypeScript + Tailwind",
    "FastAPI (Python)",
    "PostgreSQL",
    "Auth: JWT",
    "Docker + AWS/Azure",
    "GenAI: Gemini API",
]


async def suggest_tech_stack(srs_text: str) -> Dict:
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    model = settings.GEMINI_MODEL

    if not api_key:
        return {"tech_stack": DEFAULT_TECH_STACK}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": f"SRS:\n{srs_text[:8000]}"},
                ]
            }
        ],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 256},
    }

    params = {"key": api_key}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            parsed = coerce_tech_stack(text)
            return parsed or {"tech_stack": DEFAULT_TECH_STACK}
    except Exception:
        return {"tech_stack": DEFAULT_TECH_STACK}


def coerce_tech_stack(text: str) -> Dict:
    try:
        obj = json.loads(text)
        return {"tech_stack": list(obj.get("tech_stack", DEFAULT_TECH_STACK))}
    except Exception:
        pass
    tech_stack: List[str] = []
    for line in text.splitlines():
        line_clean = line.strip("- *\t ")
        low = line_clean.lower()
        if any(k in low for k in [
            "react", "next.js", "vue", "angular", "fastapi", "django", "flask",
            "node", "express", "postgres", "mysql", "mongodb", "tailwind",
            "docker", "kubernetes", "aws", "azure", "gcp", "gemini", "openai"
        ]):
            tech_stack.append(line_clean)
    return {"tech_stack": list(dict.fromkeys(tech_stack)) or DEFAULT_TECH_STACK}
