from typing import List, Dict


def estimate_fp(requirements: List[Dict]) -> Dict:
    # Simple heuristic: count types
    inputs = sum(1 for r in requirements if any(
        k in r["requirement"].lower() for k in ["input", "enter", "add", "submit"]))
    outputs = sum(1 for r in requirements if any(k in r["requirement"].lower(
    ) for k in ["output", "report", "display", "show", "export"]))
    data_entities = sum(1 for r in requirements if any(k in r["requirement"].lower(
    ) for k in ["record", "entity", "table", "database", "data"]))
    fp = 4 * inputs + 5 * outputs + 7 * data_entities
    return {
        "inputs": inputs,
        "outputs": outputs,
        "data_entities": data_entities,
        "function_points": fp,
    }
