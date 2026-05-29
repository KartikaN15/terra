"""Feature extraction stub"""
from typing import Dict, Any


def extract_features(metadata: Dict[str, Any]) -> Dict[str, float]:
    return {
        "duration": float(metadata.get("duration", 30)),
        "headcount": float(metadata.get("headcount", 50)),
        "output_units": float(metadata.get("output_units", 1)),
    }
