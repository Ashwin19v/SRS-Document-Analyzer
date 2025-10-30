import re
from collections import Counter
from typing import Dict, List

try:
    import spacy  # type: ignore
    _NLP = None
except Exception:
    spacy = None  # type: ignore
    _NLP = None

# Minimal English stopword set to avoid runtime downloads
STOPWORDS = set(
    (
        "a an the and or but if then else for while of in on at by with to from is are was were "
        "be been being do does did not no nor so than too very can will just into over under between "
        "out up down off again further once here there when where why how all any both each few more "
        "most other some such only own same s o t don should now you your yours yourself yourselves "
        "he him his himself she her hers herself it its itself we us our ours ourselves they them their "
        "theirs themselves i me my mine myself this that these those as until about against during before "
        "after above below having have has had doing having"
    ).split()
)

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]+")


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def top_keywords(text: str, k: int = 15) -> List[str]:
    tokens = [t for t in tokenize(text) if t not in STOPWORDS and len(t) > 2]
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(k)]


def _ensure_spacy():
    global _NLP
    if _NLP is not None:
        return _NLP
    if spacy is None:
        _NLP = None
        return None
    try:
        _NLP = spacy.load("en_core_web_sm")
    except Exception:
        # Model not installed; no NER
        _NLP = None
    return _NLP


def extract_entities(text: str) -> List[Dict[str, str]]:
    nlp_engine = _ensure_spacy()
    ents: List[Dict[str, str]] = []
    if nlp_engine is None:
        return ents
    doc = nlp_engine(text[:200000])
    for e in doc.ents:
        ents.append({"text": e.text, "label": e.label_})
    return ents


def analyze_text(text: str) -> Dict:
    tokens = tokenize(text)
    return {
        "word_count": len(tokens),
        "keywords": top_keywords(text, 12),
        "entities": extract_entities(text),
    }
