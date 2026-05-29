"""Tests for train report persistence and model versioning."""
import pytest
import os
import json
from ml_engine.pipeline import MLPipeline


def test_train_report_exists():
    model_dir = os.environ.get("MODEL_DIR", "./models")
    manifest_path = os.path.join(model_dir, "pipeline_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            data = json.load(f)
        assert "greenlight_version" in data or "greenlight" in data
    else:
        pytest.skip("No trained model found")


def test_pipeline_can_load_greenlight():
    pipeline = MLPipeline.for_domain("film_tv")
    version = pipeline.get_latest_version()
    if version:
        pipeline.greenlight.load(version)
        assert pipeline.greenlight.model is not None
    else:
        pytest.skip("No greenlight version to load")
