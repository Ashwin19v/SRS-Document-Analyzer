import re
from typing import List, Dict

RE_REQUIREMENT = re.compile(
    r"(?:shall|must|should|will|can|may)\s+([^.]+\.)", re.IGNORECASE)

COMPLEXITY_KEYWORDS = {
    "Low": ["simple", "basic", "view", "list", "read"],
    "Medium": ["edit", "update", "search", "filter", "access", "manage"],
    "High": [
        "integrate", "sync", "real-time", "security", "payment",
        "predict", "analyze", "AI", "ML"
    ],
}


def extract_requirements(text: str) -> List[Dict]:
    requirements = []
    for match in RE_REQUIREMENT.finditer(text):
        req = match.group(1).strip()
        complexity = "Low"
        for level, kws in COMPLEXITY_KEYWORDS.items():
            if any(kw in req.lower() for kw in kws):
                complexity = level
        requirements.append({
            "requirement": req,
            "complexity": complexity,
            "features": {
                "matched_keywords": [
                    kw
                    for kws in COMPLEXITY_KEYWORDS.values()
                    for kw in kws
                    if kw in req.lower()
                ],
                "word_count": len(req.split()),
            },
        })
    return requirements
