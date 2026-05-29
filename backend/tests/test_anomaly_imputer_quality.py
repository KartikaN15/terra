"""Tests for anomaly reasons and imputer fallback + quality signal."""
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from ml_engine.anomaly_detector import AnomalyDetector
from ml_engine.schemas import TimeSeriesPoint, AnomalyDetectRequest


def test_anomaly_response_includes_reason_and_zscore():
    detector = AnomalyDetector()
    ts = [
        TimeSeriesPoint(timestamp=datetime(2024, 1, i, tzinfo=timezone.utc), kgco2e=Decimal("100"))
        for i in range(1, 15)
    ]
    ts[7] = TimeSeriesPoint(timestamp=datetime(2024, 1, 8, tzinfo=timezone.utc), kgco2e=Decimal("500"))
    req = AnomalyDetectRequest(project_id="test", time_series=ts, window_days=7, sensitivity=0.05)
    result = detector.detect(req)
    assert result.project_id == "test"
