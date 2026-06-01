"""Greenlight Predictor.

Loads the trained XGBoost greenlight model (target = natural-log of total
kgCO2e), its fitted feature extractor, and a bootstrap ensemble used to derive
a prediction interval. Predictions are returned in tCO2e (kg / 1000).
"""
import os
import math
from decimal import Decimal
from typing import List, Optional

import numpy as np
import joblib
import xgboost as xgb

from .schemas import GreenlightPredictRequest, GreenlightPredictResult
from .features import build_feature_frame, MODEL_FEATURE_ORDER

# How many bootstrap models a trained version may carry.
_MAX_BOOTSTRAP = 50

# Human-friendly labels for the model's feature columns (for top-driver output).
_FEATURE_LABELS = {
    "cat_project_type": "Project type",
    "cat_scale_band": "Budget band",
    "cat_complexity": "Complexity",
    "cat_region": "Region",
    "num_duration": "Duration",
    "num_headcount": "Headcount",
    "num_output_units": "Output units",
    "num_output_size": "Output size",
}


class ShapAttribution:
    """Lightweight per-feature attribution carrier (callers read `.feature`)."""

    def __init__(self, feature: str, value: float):
        self.feature = feature
        self.value = value


class GreenlightPredictor:
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.model: Optional[xgb.Booster] = None
        self._extractor = None
        self._bootstrap: List[xgb.Booster] = []
        self._model_version = ""

    def load(self, version: str):
        """Load a trained model bundle (model.json + extractor.joblib +
        bootstrap_*.json) from ``<model_dir>/<version>``."""
        base = os.path.join(self.model_dir, version)
        booster = xgb.Booster()
        booster.load_model(os.path.join(base, "model.json"))
        extractor = joblib.load(os.path.join(base, "extractor.joblib"))

        bootstrap: List[xgb.Booster] = []
        for i in range(_MAX_BOOTSTRAP):
            path = os.path.join(base, f"bootstrap_{i}.json")
            if not os.path.exists(path):
                break
            b = xgb.Booster()
            b.load_model(path)
            bootstrap.append(b)

        # Commit only once everything loaded, so a partial failure leaves the
        # predictor in its previous (possibly unloaded) state.
        self.model = booster
        self._extractor = extractor
        self._bootstrap = bootstrap
        self._model_version = version

    def _dmatrix(self, request: GreenlightPredictRequest) -> xgb.DMatrix:
        meta = request.metadata
        metadata = {
            "project_type": meta.project_type,
            "scale_band": meta.scale_band,
            "complexity": meta.complexity,
            "region": meta.region,
            "duration": meta.duration,
            "headcount": meta.headcount,
            "output_units": meta.output_units,
            "output_size": meta.output_size,
        }
        frame = build_feature_frame(self._extractor, metadata)
        return xgb.DMatrix(frame, feature_names=MODEL_FEATURE_ORDER)

    @staticmethod
    def _kg_to_tco2e(log_kg: float) -> float:
        # Target was trained as the natural log of total kgCO2e.
        return math.exp(log_kg) / 1000.0

    def predict(self, request: GreenlightPredictRequest) -> GreenlightPredictResult:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        dmatrix = self._dmatrix(request)
        point_tco2e = self._kg_to_tco2e(float(self.model.predict(dmatrix)[0]))

        # Prediction interval from the bootstrap ensemble's spread. Falls back to
        # a ±25% band when no bootstrap models are present.
        if self._bootstrap:
            boot = sorted(self._kg_to_tco2e(float(b.predict(dmatrix)[0])) for b in self._bootstrap)
            lower = float(np.percentile(boot, 5))
            upper = float(np.percentile(boot, 95))
        else:
            lower, upper = point_tco2e * 0.75, point_tco2e * 1.25

        # Keep the point estimate inside its own interval.
        lower = min(lower, point_tco2e)
        upper = max(upper, point_tco2e)

        # Confidence: tighter relative interval → higher confidence. Mapped into
        # a sensible [0.5, 0.95] band.
        rel_width = (upper - lower) / point_tco2e if point_tco2e > 0 else 1.0
        confidence = max(0.5, min(0.95, 1.0 - rel_width / 2.0))

        # Top driver via SHAP contributions (last column is the bias term).
        contribs = self.model.predict(dmatrix, pred_contribs=True)[0]
        feature_contribs = contribs[:-1]
        order = np.argsort(np.abs(feature_contribs))[::-1]
        shap = [
            ShapAttribution(
                feature=_FEATURE_LABELS.get(MODEL_FEATURE_ORDER[i], MODEL_FEATURE_ORDER[i]),
                value=float(feature_contribs[i]),
            )
            for i in order
        ]

        return GreenlightPredictResult(
            project_id=request.project_id,
            predicted_total_tco2e=Decimal(str(round(point_tco2e, 2))),
            interval_lower_tco2e=Decimal(str(round(lower, 2))),
            interval_upper_tco2e=Decimal(str(round(upper, 2))),
            confidence=Decimal(str(round(confidence, 2))),
            shap_attribution=shap,
            model_version=self._model_version,
        )
