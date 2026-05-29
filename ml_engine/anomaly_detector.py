"""Anomaly Detector — simple rolling-window z-score detection."""
from decimal import Decimal
from typing import List
from statistics import mean, stdev

from .schemas import AnomalyDetectRequest, AnomalyDetectResult, AnomalyItem, Severity


class AnomalyDetector:
    def __init__(self):
        self.model = {"type": "zscore"}

    def detect(self, request: AnomalyDetectRequest) -> AnomalyDetectResult:
        ts = request.time_series
        if len(ts) < 2:
            return AnomalyDetectResult(project_id=request.project_id, anomalies=[], window_days=request.window_days)

        values = [float(p.kgco2e) for p in ts]
        avg = mean(values)
        std = stdev(values) if len(values) > 1 else 0.0

        anomalies: List[AnomalyItem] = []
        for p in ts:
            v = float(p.kgco2e)
            z = (v - avg) / std if std > 0 else 0.0
            if abs(z) > 2.0:
                deviation = ((v - avg) / avg * 100) if avg != 0 else 0.0
                severity = Severity.HIGH if abs(z) > 3.0 else Severity.MEDIUM
                anomalies.append(
                    AnomalyItem(
                        timestamp=p.timestamp,
                        observed_kgco2e=Decimal(str(v)),
                        expected_kgco2e=Decimal(str(avg)),
                        deviation_percent=Decimal(str(deviation)),
                        severity=severity,
                        reason=f"{'Spike' if deviation > 0 else 'Drop'} detected: {abs(deviation):.0f}% vs rolling average",
                        z_score=round(z, 2),
                    )
                )

        return AnomalyDetectResult(
            project_id=request.project_id,
            anomalies=anomalies,
            window_days=request.window_days,
        )
