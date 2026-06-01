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
        self.greenlight = GreenlightPredictor(model_dir=model_dir)
        self.imputer = CategoryImputer()
        self.anomaly = AnomalyDetector()

    @classmethod
    def for_domain(cls, domain: str, model_dir: str = "./models"):
        return cls(domain, model_dir)

    def get_latest_version(self) -> Optional[str]:
        """Resolve the newest greenlight model version.

        Prefer an explicit ``greenlight_version`` in the pipeline manifest, but
        fall back to scanning the model dir for ``glp-*`` bundles (the manifest
        historically didn't record the version string, which left valid models
        on disk undiscoverable). The newest bundle by mtime wins.
        """
        manifest_path = os.path.join(self.model_dir, "pipeline_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                version = data.get("greenlight_version")
                if version and os.path.isdir(os.path.join(self.model_dir, version)):
                    return version
            except Exception:
                pass

        try:
            candidates = [
                d for d in os.listdir(self.model_dir)
                if d.startswith("glp-") and os.path.isdir(os.path.join(self.model_dir, d))
                and os.path.exists(os.path.join(self.model_dir, d, "model.json"))
            ]
        except OSError:
            return None
        if not candidates:
            return None
        return max(candidates, key=lambda d: os.path.getmtime(os.path.join(self.model_dir, d)))

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
