from typing import Literal

# Basic COCOMO model parameters
PARAMS = {
    "organic": {"a": 2.4, "b": 1.05, "c": 2.5, "d": 0.38},
    "semidetached": {"a": 3.0, "b": 1.12, "c": 2.5, "d": 0.35},
    "embedded": {"a": 3.6, "b": 1.20, "c": 2.5, "d": 0.32},
}

Mode = Literal["organic", "semidetached", "embedded"]


def estimate(word_count: int, mode: Mode = "organic", rate_per_pm_usd: int = 12000):
    """
    Estimate cost using Basic COCOMO.

    We don't have KLOC; approximate it from SRS word count. This is a coarse proxy and should be
    calibrated per organization. Adjust divisor to tune sensitivity.
    """
    p = PARAMS[mode]
    # Very rough proxy: assume 1 KLOC per 5000 words of SRS
    kloc = max(0.5, word_count / 5000.0)
    effort_pm = p["a"] * (kloc ** p["b"])  # Person-Months
    time_months = p["c"] * (effort_pm ** p["d"])  # Development Time in months
    cost_usd = effort_pm * rate_per_pm_usd
    # Convert to weeks
    weeks = int(round(time_months * 4.345, 0))
    return {
        "kloc_estimate": round(kloc, 2),
        "effort_pm": round(effort_pm, 1),
        "time_weeks": weeks,
        "cost_usd": int(cost_usd),
    }
