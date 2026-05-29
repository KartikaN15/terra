"""Greenlight Predictor stub"""
import os
import json
from decimal import Decimal
from typing import Optional, Any

from .schemas import GreenlightPredictRequest, GreenlightPredictResult


class GreenlightPredictor:
    def __init__(self):
        self.model = None
        self._model_version = ""
        self._bootstrap_models = []

    def load(self, version: str):
        """Load a trained model by version string."""
        self._model_version = version
        self.model = {"version": version}  # stub

    def predict(self, request: GreenlightPredictRequest) -> GreenlightPredictResult:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        # Stub prediction
        return GreenlightPredictResult(
            project_id=request.project_id,
            predicted_total_tco2e=Decimal("100.0"),
            interval_lower_tco2e=Decimal("80.0"),
            interval_upper_tco2e=Decimal("120.0"),
            confidence=Decimal("0.75"),
            model_version=self._model_version,
        )
