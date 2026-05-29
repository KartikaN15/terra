"""ML Pipeline stub"""
import os
import json
from decimal import Decimal
from typing import List, Dict, Any, Optional

from .schemas import GreenlightPredictRequest, GreenlightPredictResult, AnomalyDetectRequest, AnomalyDetectResult, Severity, AnomalyItem
from .greenlight_predictor import GreenlightPredictor
from .category_imputer import CategoryImputer
from .anomaly_detector import AnomalyDetector


class MLPipeline:
    def __init__(self, domain: str, model_dir: str):
        self.domain = domain
        self.model_dir = model_dir
        self.greenlight = GreenlightPredictor()
        self.imputer = CategoryImputer()
        self.anomaly = AnomalyDetector()

    @classmethod
    def for_domain(cls, domain: str, model_dir: str = "./models"):
        return cls(domain, model_dir)

    def get_latest_version(self) -> Optional[str]:
        manifest_path = os.path.join(self.model_dir, "pipeline_manifest.json")
        if not os.path.exists(manifest_path):
            return None
        try:
            with open(manifest_path) as f:
                data = json.load(f)
            return data.get("greenlight_version")
        except Exception:
            return None

    def train_all(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train all models. Returns metrics dict."""
        # Stub: no-op training
        return {
            "greenlight": {"r2": Decimal("0.0"), "mae_tco2e": Decimal("0.0"), "calibrated": False},
            "imputer": {"accuracy": Decimal("0.0")},
        }

    def predict_greenlight(self, request: GreenlightPredictRequest) -> GreenlightPredictResult:
        if self.greenlight.model is None:
            raise RuntimeError("Greenlight model not loaded")
        return self.greenlight.predict(request)

    def detect_anomalies(self, request: AnomalyDetectRequest) -> AnomalyDetectResult:
        return self.anomaly.detect(request)
