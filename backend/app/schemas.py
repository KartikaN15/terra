"""
Pydantic schemas for API request/response validation.
Separated from ml_engine.schemas   — these are for the REST API layer.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Production
# ============================================================================

class ProductionBase(BaseModel):
    title: str
    type: str
    genre: Optional[str] = None
    budget_band: Optional[str] = None
    runtime_min: Optional[int] = None
    episodes: int = 1
    shoot_days: Optional[int] = None
    locations: Optional[List[str]] = Field(default_factory=list)
    cast_count: Optional[int] = None
    crew_count: Optional[int] = None
    vfx_intensity: Optional[str] = None
    status: str = "DEVELOPMENT"
    carbon_budget_tco2e: Optional[Decimal] = None
    carbon_budget_source: Optional[str] = None


class ProductionCreate(ProductionBase):
    production_id: Optional[str] = None


class ProductionUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: Optional[str] = None
    genre: Optional[str] = None
    budget_band: Optional[str] = None
    runtime_min: Optional[int] = None
    episodes: Optional[int] = None
    shoot_days: Optional[int] = None
    locations: Optional[List[str]] = None
    cast_count: Optional[int] = None
    crew_count: Optional[int] = None
    vfx_intensity: Optional[str] = None
    status: Optional[str] = None
    carbon_budget_tco2e: Optional[Decimal] = None
    planner_state: Optional[Dict[str, Any]] = None


class ProductionOut(ProductionBase):
    model_config = ConfigDict(from_attributes=True)

    production_id: str
    created_at: datetime
    updated_at: datetime


class ProductionSummaryOut(BaseModel):
    production_id: str
    total_tco2e: Decimal
    scope_breakdown: Dict[str, Decimal]
    category_breakdown: Dict[str, Decimal]
    phase_breakdown: Dict[str, Decimal]
    overall_confidence: Decimal
    budget_variance_percent: Optional[Decimal]
    intensity_tco2e_per_hour: Optional[Decimal]
    intensity_tco2e_per_episode: Optional[Decimal]
    event_count: int
    tier_1_percent: float
    tier_2_percent: float
    tier_3_percent: float


# ============================================================================
# Activity Event
# ============================================================================

class ActivityEventBase(BaseModel):
    phase: str
    scope: Optional[str] = None
    category: str
    subcategory: str
    value: Decimal
    unit: str
    source_type: str
    source_reference: Optional[str] = None
    grid_region: Optional[str] = None
    recorded_at: datetime
    notes: Optional[str] = None


class ActivityEventCreate(ActivityEventBase):
    production_id: str
    recorded_by: str


class ActivityEventUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    phase: Optional[str] = None
    scope: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    value: Optional[Decimal] = None
    unit: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    grid_region: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class ActivityEventOut(ActivityEventBase):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    production_id: str
    kgco2e: Decimal
    kgco2e_wtt: Optional[Decimal]
    confidence_tier: str
    confidence_score: Decimal
    emission_factor_id: Optional[str]
    emission_factor_version: str
    calculation_method: str
    calculated_at: datetime
    gwp_version: Optional[str] = None
    region_match: Optional[str] = None
    unit_converted: Optional[bool] = False


class BulkEventCreate(BaseModel):
    production_id: str
    recorded_by: str
    events: List[ActivityEventCreate]


class BulkEventResult(BaseModel):
    filename: str
    total_rows: int
    created: int
    errors: List[Dict[str, Any]]


# ============================================================================
# Emission Factor
# ============================================================================

class EmissionFactorBase(BaseModel):
    standard: str
    category: str
    subcategory: str
    activity_type: str
    factor_value: Decimal
    unit: str
    scope: str
    region: str = "Global"
    country_code: Optional[str] = None
    grid_intensity_g_co2_kwh: Optional[Decimal] = None
    valid_from: datetime
    valid_to: Optional[datetime] = None
    version: str
    description: str
    radiative_forcing_multiplier: Decimal = Decimal("1.0")
    wtt_factor: Optional[Decimal] = None


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorOut(EmissionFactorBase):
    model_config = ConfigDict(from_attributes=True)
    factor_id: str
    is_active: bool


# ============================================================================
# Document
# ============================================================================

class DocumentBase(BaseModel):
    doc_type: str
    filename: str
    mime_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    production_id: str
    uploaded_by: str


class DocumentOut(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    doc_id: str
    production_id: str
    ocr_status: str
    extracted_confidence: Optional[Decimal]
    extracted_data: Optional[Dict[str, Any]] = None
    review_status: str
    uploaded_at: datetime
    linked_event_ids: Optional[List[str]] = None


# ============================================================================
# ML Requests / Responses (wrap ml_engine schemas for API)
# ============================================================================

class MLProjectMetadata(BaseModel):
    project_type: str
    scale_band: str
    duration: int
    headcount: int
    complexity: Optional[str] = None
    output_units: int = 1
    output_size: Optional[float] = None
    region: str = "UK"


class GreenlightForecastRequest(BaseModel):
    project_id: str
    metadata: MLProjectMetadata


class GreenlightForecastResponse(BaseModel):
    project_id: str
    predicted_total_tco2e: Decimal
    interval_lower_tco2e: Decimal
    interval_upper_tco2e: Decimal
    confidence: Decimal
    top_driver: str
    model_version: str


class CategoryImputeRequestAPI(BaseModel):
    project_id: str
    metadata: MLProjectMetadata
    known_categories: List[Dict[str, Any]]
    missing_categories: List[str]


class AnomalyDetectRequestAPI(BaseModel):
    project_id: str
    time_series: List[Dict[str, Any]]
    window_days: int = 7
    sensitivity: float = 0.05


# ============================================================================
# Auth
# ============================================================================

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============================================================================
# Notification
# ============================================================================

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: str
    user_id: Optional[str] = None
    type: str
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationMarkRead(BaseModel):
    is_read: bool = True


class NotificationListOut(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationOut]
