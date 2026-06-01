"""Feature extraction for the Greenlight predictor.

The trained extractor (``extractor.joblib``) is a dict carrying a fitted
sklearn ``OrdinalEncoder`` (categoricals), a ``StandardScaler`` (numericals)
and a :class:`DomainConfig`. ``DomainConfig`` must exist here with the same
attribute layout so the artifact unpickles. ``build_feature_frame`` reproduces
the training-time column order the XGBoost model expects:

    cat_project_type, cat_scale_band, cat_complexity, cat_region,
    num_duration, num_headcount, num_output_units, num_output_size
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

import pandas as pd

# Column order the encoder/scaler were fitted on (see extractor.joblib).
CATEGORICAL_FEATURES = ["project_type", "scale_band", "complexity", "region"]
NUMERICAL_FEATURES = ["duration", "headcount", "output_units", "output_size"]

# Final feature order consumed by the model (prefixed cat_/num_).
MODEL_FEATURE_ORDER = [f"cat_{c}" for c in CATEGORICAL_FEATURES] + [
    f"num_{n}" for n in NUMERICAL_FEATURES
]

# Neutral defaults when a numerical field is missing. The scaler centres these,
# so a missing value lands near the training mean rather than skewing the row.
_NUMERIC_DEFAULTS = {"duration": 30.0, "headcount": 50.0, "output_units": 1.0, "output_size": 90.0}


@dataclass
class DomainConfig:
    """Maps a domain's raw project fields onto the model's generic feature
    slots. Persisted inside the extractor artifact; kept here so it unpickles."""

    domain_name: str = "film_tv"
    project_type_field: str = "genre"
    scale_band_field: str = "budget_band"
    duration_field: str = "shoot_days"
    headcount_field: str = "crew_count"
    complexity_field: str = "vfx_intensity"
    output_units_field: str = "episodes"
    output_size_field: str = "runtime_min"
    region_field: str = "primary_region"
    categorical_features: List[str] = field(default_factory=lambda: list(CATEGORICAL_FEATURES))
    numerical_features: List[str] = field(default_factory=lambda: list(NUMERICAL_FEATURES))


def _coerce_categorical(value: Any) -> str:
    """Encoder was fitted on strings; missing → empty string, which the
    encoder maps to its `unknown_value` (-1) rather than erroring."""
    return "" if value is None else str(value)


def _coerce_numerical(name: str, value: Any) -> float:
    if value is None:
        return _NUMERIC_DEFAULTS.get(name, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return _NUMERIC_DEFAULTS.get(name, 0.0)


def build_feature_frame(extractor: Dict[str, Any], metadata: Dict[str, Any]) -> pd.DataFrame:
    """Transform a project metadata dict into the single-row feature frame the
    model expects. Uses the fitted encoder/scaler from ``extractor`` and passes
    named DataFrames so sklearn doesn't warn about missing feature names."""
    cat_encoder = extractor["cat_encoder"]
    num_scaler = extractor["num_scaler"]

    cat_in = pd.DataFrame(
        [[_coerce_categorical(metadata.get(c)) for c in CATEGORICAL_FEATURES]],
        columns=CATEGORICAL_FEATURES,
    )
    num_in = pd.DataFrame(
        [[_coerce_numerical(n, metadata.get(n)) for n in NUMERICAL_FEATURES]],
        columns=NUMERICAL_FEATURES,
    )

    cat_enc = cat_encoder.transform(cat_in)
    num_sc = num_scaler.transform(num_in)

    row = list(cat_enc[0]) + list(num_sc[0])
    return pd.DataFrame([row], columns=MODEL_FEATURE_ORDER)


# Legacy stub kept for callers that imported the old helper.
def extract_features(metadata: Dict[str, Any]) -> Dict[str, float]:
    return {
        "duration": float(metadata.get("duration", 30)),
        "headcount": float(metadata.get("headcount", 50)),
        "output_units": float(metadata.get("output_units", 1)),
    }
