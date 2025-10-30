from __future__ import annotations
from typing import Dict, List
import os
import joblib
from dataclasses import dataclass

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained_model.joblib")

FEATURES = {
    "auth": ["auth", "authentication", "oauth", "jwt", "sso"],
    "payments": ["payment", "stripe", "paypal", "billing"],
    "realtime": ["realtime", "websocket", "stream", "socket"],
    "ml": ["ml", "machine learning", "model", "classify", "predict"],
    "mobile": ["mobile", "android", "ios", "react native", "flutter"],
    "api": ["api", "rest", "graphql"],
    "db": ["database", "db", "postgres", "mysql", "mongodb", "sql"],
}


@dataclass
class Prediction:
    time_weeks: int
    software_needed: List[str]
    custom_model_plan: str


def featurize(text: str) -> Dict[str, int]:
    low = text.lower()
    feats: Dict[str, int] = {}
    for name, kws in FEATURES.items():
        feats[name] = int(any(k in low for k in kws))
    feats["length_k"] = int(len(text.split()) / 1000)
    return feats


def train_if_needed():
    """Train a tiny heuristic 'model' if no trained artifact exists.
    To keep dependencies light and avoid requiring a dataset, we persist a simple config.
    """
    if os.path.exists(MODEL_PATH):
        return
    # We store simple weights for features that influence time estimation
    weights = {
        "base_weeks": 4,
        "auth": 1,
        "payments": 2,
        "realtime": 2,
        "ml": 3,
        "mobile": 2,
        "api": 1,
        "db": 1,
        "per_length_k": 1,
    }
    joblib.dump(weights, MODEL_PATH)


def predict(text: str) -> Prediction:
    train_if_needed()
    weights = joblib.load(MODEL_PATH)
    feats = featurize(text)
    weeks = int(weights["base_weeks"] + sum(weights.get(k, 0) * feats.get(k, 0)
                for k in FEATURES.keys()) + feats["length_k"] * weights["per_length_k"])
    weeks = max(2, min(weeks, 52))

    software: List[str] = ["Node.js 18+", "Python 3.10+", "Docker"]
    if feats["db"]:
        software.append("PostgreSQL or managed DB")
    if feats["ml"]:
        software.append("Python ML stack (scikit-learn / transformers)")
    if feats["mobile"]:
        software.append("Android Studio / Xcode (if native)")
    if feats["realtime"]:
        software.append("Redis / WebSocket gateway")

    plan = (
        "Custom model pipeline: feature extraction from requirements (TF-IDF / embeddings), "
        "baseline classifier for requirement types; extend with NER-based slot filling to capture entities. "
        "Create labeled set from past SRS; train and evaluate with F1; integrate behind FastAPI; "
        "set up monitoring and periodic retraining."
    )

    return Prediction(time_weeks=weeks, software_needed=software, custom_model_plan=plan)
