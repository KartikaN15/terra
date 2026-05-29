"""ml_engine schemas"""
from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class ProjectMetadata:
    project_type: str
    scale_band: str
    duration: int
    headcount: int
    complexity: Optional[str] = None
    output_units: int = 1
    output_size: Optional[float] = None
    region: str = "UK"


@dataclass
class GreenlightPredictRequest:
    project_id: str
    metadata: ProjectMetadata


@dataclass
class GreenlightPredictResult:
    project_id: str
    predicted_total_tco2e: Decimal
    interval_lower_tco2e: Decimal
    interval_upper_tco2e: Decimal
    confidence: Decimal
    shap_attribution: List[Any] = field(default_factory=list)
    model_version: str = ""


@dataclass
class TimeSeriesPoint:
    timestamp: datetime
    kgco2e: Decimal


@dataclass
class AnomalyDetectRequest:
    project_id: str
    time_series: List[TimeSeriesPoint]
    window_days: int = 7
    sensitivity: float = 0.05


@dataclass
class AnomalyItem:
    timestamp: datetime
    observed_kgco2e: Decimal
    expected_kgco2e: Decimal
    deviation_percent: Decimal
    severity: Severity
    reason: str = ""
    z_score: Optional[float] = None


@dataclass
class AnomalyDetectResult:
    project_id: str
    anomalies: List[AnomalyItem]
    window_days: int = 7
