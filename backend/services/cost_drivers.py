from typing import Dict

COST_DRIVER_FACTORS = {
    "real_time": 1.25,
    "security": 1.15,
    "performance": 1.10,
    "complex_logic": 1.20,
}


def detect_cost_drivers(text: str) -> Dict:
    detected = {}
    eaf = 1.0
    for k, v in COST_DRIVER_FACTORS.items():
        if k.replace('_', ' ') in text.lower():
            detected[k] = v
            eaf *= v
    return {"EAF": round(eaf, 2), "detected": detected}
