"""
SQLAlchemy ORM Models
Domain-agnostic: works for film/tv, construction, logistics, etc.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, DateTime, Numeric, Integer, ForeignKey, Text, Enum,
    Index, JSON, UniqueConstraint, Boolean, event,
)

from sqlalchemy.orm import relationship

from .database import Base


class AuditIntegrityError(ValueError):
    """Raised when an ActivityEvent is missing audit fields required by CLAUDE.md."""


class Production(Base):
    __tablename__ = "productions"

    production_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String(50), nullable=False, default="film_tv")
    title = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    genre = Column(String(50))
    budget_band = Column(String(50))
    runtime_min = Column(Integer)
    episodes = Column(Integer, default=1)
    shoot_days = Column(Integer)
    locations = Column(JSON, default=list)
    cast_count = Column(Integer)
    crew_count = Column(Integer)
    vfx_intensity = Column(String(50))
    status = Column(String(50), default="DEVELOPMENT")

    # Carbon targets
    carbon_budget_tco2e = Column(Numeric(12, 4))
    carbon_budget_source = Column(String(50))

    # Visual planner state (ReactFlow nodes + edges)
    planner_state = Column(JSON)

    # Audit
    created_by = Column(String(36))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    events = relationship("ActivityEvent", back_populates="production", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="production", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_productions_domain_status", "domain", "status"),
    )


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.production_id", ondelete="CASCADE"), nullable=False)

    phase = Column(String(50), nullable=False)
    scope = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), nullable=False)

    value = Column(Numeric(15, 6), nullable=False)
    unit = Column(String(50), nullable=False)
    kgco2e = Column(Numeric(15, 6), nullable=False)
    kgco2e_wtt = Column(Numeric(15, 6))

    confidence_tier = Column(String(50), nullable=False)
    confidence_score = Column(Numeric(3, 2), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_reference = Column(Text)

    emission_factor_id = Column(String(36), ForeignKey("emission_factors.factor_id"), nullable=False)
    emission_factor_version = Column(String(100), nullable=False)
    # Audit signals from the calculation engine   — let downstream queries
    # ("show me events that fell back to a global factor") run without
    # re-deriving the lookup state.
    gwp_version = Column(String(20))                 # AR5, AR6, etc.   — sourced from factor
    region_match = Column(String(20))                # exact | region_fallback | global_fallback
    unit_converted = Column(Boolean, default=False)

    location_id = Column(String(36))
    grid_region = Column(String(50))

    recorded_by = Column(String(36), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text)

    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    calculation_method = Column(String(100), nullable=False)

    # Relationships
    production = relationship("Production", back_populates="events")
    emission_factor = relationship("EmissionFactor")

    __table_args__ = (
        Index("idx_events_production", "production_id", "category"),
        Index("idx_events_scope", "production_id", "scope"),
        Index("idx_events_confidence", "confidence_tier"),
    )


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    standard = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), nullable=False)
    activity_type = Column(String(100), nullable=False)

    factor_value = Column(Numeric(15, 8), nullable=False)
    unit = Column(String(50), nullable=False)
    scope = Column(String(50), nullable=False)

    region = Column(String(50), nullable=False, default="Global")
    country_code = Column(String(2))
    grid_intensity_g_co2_kwh = Column(Numeric(10, 4))

    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True))
    version = Column(String(100), nullable=False)

    source_url = Column(Text)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    radiative_forcing_multiplier = Column(Numeric(3, 2), default=1.0)
    wtt_factor = Column(Numeric(15, 8))
    # GWP basis (AR5, AR6, …). Factors get re-baselined as the IPCC publishes
    # new assessment reports; persisting the basis lets us re-cost old events
    # when we adopt a newer set without losing audit history.
    gwp_version = Column(String(20), default="AR5")

    __table_args__ = (
        UniqueConstraint("standard", "category", "subcategory", "region", "version"),
        Index("idx_factors_lookup", "category", "subcategory", "region", "is_active"),
    )


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.production_id", ondelete="CASCADE"), nullable=False)

    doc_type = Column(String(50), nullable=False)
    s3_path = Column(Text)
    filename = Column(Text, nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))

    ocr_status = Column(String(50), default="PENDING")
    extracted_raw_text = Column(Text)
    extracted_data = Column(JSON)
    extracted_confidence = Column(Numeric(3, 2))
    extracted_by_model = Column(String(100))

    review_status = Column(String(50), default="PENDING")
    reviewed_by = Column(String(36))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)

    linked_event_ids = Column(JSON, default=list)

    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    uploaded_by = Column(String(36), nullable=False)

    production = relationship("Production", back_populates="documents")


class User(Base):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(36))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "is_read"),
        Index("idx_notifications_created", "created_at"),
    )


def _require_audit_fields(_mapper, _connection, target: "ActivityEvent") -> None:
    # CLAUDE.md guardrail: never persist an emission calculation without
    # both the factor id and version, so any number on screen can be re-derived.
    factor_id = getattr(target, "emission_factor_id", None)
    factor_version = getattr(target, "emission_factor_version", None)
    if not factor_id or not str(factor_id).strip():
        raise AuditIntegrityError(
            "ActivityEvent.emission_factor_id is required for audit integrity"
        )
    if not factor_version or not str(factor_version).strip():
        raise AuditIntegrityError(
            "ActivityEvent.emission_factor_version is required for audit integrity"
        )


event.listen(ActivityEvent, "before_insert", _require_audit_fields)
event.listen(ActivityEvent, "before_update", _require_audit_fields)
