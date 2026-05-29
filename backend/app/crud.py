"""CRUD operations."""
from decimal import Decimal
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_production(db: Session, production_id: str):
    return db.query(models.Production).filter(models.Production.production_id == production_id).first()

def get_productions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Production).offset(skip).limit(limit).all()

def create_production(db: Session, prod: schemas.ProductionCreate, created_by: str):
    db_prod = models.Production(**prod.model_dump(exclude_unset=True), created_by=created_by)
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod

def update_production(db: Session, production_id: str, updates: schemas.ProductionUpdate):
    db_prod = get_production(db, production_id)
    if not db_prod:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_prod, field, value)
    db.commit()
    db.refresh(db_prod)
    return db_prod


def delete_production(db: Session, production_id: str) -> bool:
    db_prod = get_production(db, production_id)
    if not db_prod:
        return False
    db.delete(db_prod)
    db.commit()
    return True


def delete_event(db: Session, event_id: str) -> bool:
    db_event = get_event(db, event_id)
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True

def get_event(db: Session, event_id: str):
    return db.query(models.ActivityEvent).filter(models.ActivityEvent.event_id == event_id).first()

def get_events_by_production(db: Session, production_id: str, skip: int = 0, limit: int = 500):
    return (
        db.query(models.ActivityEvent)
        .filter(models.ActivityEvent.production_id == production_id)
        .order_by(models.ActivityEvent.recorded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_event(
    db, event, kgco2e, confidence_tier, confidence_score,
    emission_factor_id, emission_factor_version, calculation_method,
    *, gwp_version=None, region_match=None, unit_converted=False,
):
    db_event = models.ActivityEvent(
        production_id=event.production_id, phase=event.phase, scope=event.scope,
        category=event.category, subcategory=event.subcategory, value=event.value,
        unit=event.unit, kgco2e=kgco2e, confidence_tier=confidence_tier,
        confidence_score=confidence_score, source_type=event.source_type,
        source_reference=event.source_reference, emission_factor_id=emission_factor_id,
        emission_factor_version=emission_factor_version, grid_region=event.grid_region,
        recorded_by=event.recorded_by, recorded_at=event.recorded_at,
        notes=event.notes, calculation_method=calculation_method,
        gwp_version=gwp_version, region_match=region_match,
        unit_converted=bool(unit_converted),
    )
    db.add(db_event); db.commit()
    return db_event

def update_event(db: Session, event_id: str, updates: dict) -> Optional[models.ActivityEvent]:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    for field, value in updates.items():
        if hasattr(db_event, field):
            setattr(db_event, field, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_factor(db: Session, factor_id: str):
    return db.query(models.EmissionFactor).filter(models.EmissionFactor.factor_id == factor_id).first()

def get_factors(db: Session, category=None, region=None, subcategory=None, search=None, limit=100):
    q = db.query(models.EmissionFactor)
    if category: q = q.filter(models.EmissionFactor.category == category)
    if region: q = q.filter(models.EmissionFactor.region == region)
    if subcategory: q = q.filter(models.EmissionFactor.subcategory == subcategory)
    if search:
        search_filter = f"%{search}%"
        q = q.filter(
            (models.EmissionFactor.subcategory.ilike(search_filter)) |
            (models.EmissionFactor.activity_type.ilike(search_filter)) |
            (models.EmissionFactor.standard.ilike(search_filter))
        )
    return q.limit(limit).all()

def get_best_factor(db: Session, category: str, subcategory: str, region: str, standard=None):
    """Backwards-compatible shim around the resolver: returns the factor row only.

    Prefer `resolve_factor` (returns the row + match-quality block) so callers
    can record audit signals. This wrapper exists for legacy call sites.
    """
    from .services.factor_resolver import resolve
    rf = resolve(db, category, subcategory, region, standard)
    return rf.factor if rf else None


def resolve_factor(db: Session, category: str, subcategory: str, region: str, standard=None, as_of=None):
    """Resolve the best factor with full match-quality metadata."""
    from .services.factor_resolver import resolve
    return resolve(db, category, subcategory, region, standard, as_of=as_of)

def create_factor(db: Session, factor: schemas.EmissionFactorCreate):
    db_factor = models.EmissionFactor(**factor.model_dump())
    db.add(db_factor)
    db.commit()
    db.refresh(db_factor)
    return db_factor

def create_notification(db: Session, user_id: Optional[str], type: str, title: str, message: str,
                         entity_type: Optional[str] = None, entity_id: Optional[str] = None):
    notif = models.Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_notifications(db: Session, user_id: Optional[str] = None, limit: int = 50, offset: int = 0):
    q = db.query(models.Notification)
    if user_id:
        q = q.filter(
            (models.Notification.user_id == user_id) | (models.Notification.user_id.is_(None))
        )
    else:
        q = q.filter(models.Notification.user_id.is_(None))
    total = q.count()
    items = q.order_by(models.Notification.created_at.desc()).offset(offset).limit(limit).all()
    unread = sum(1 for i in items if not i.is_read)
    return total, unread, items


def get_notification(db: Session, notification_id: str):
    return db.query(models.Notification).filter(models.Notification.notification_id == notification_id).first()


def mark_notification_read(db: Session, notification_id: str, is_read: bool = True):
    notif = get_notification(db, notification_id)
    if not notif: return None
    notif.is_read = is_read
    db.commit(); db.refresh(notif)
    return notif


def mark_all_notifications_read(db: Session, user_id: str):
    db.query(models.Notification).filter(
        (models.Notification.user_id == user_id) | (models.Notification.user_id.is_(None)),
        models.Notification.is_read == False
    ).update({models.Notification.is_read: True}, synchronize_session=False)
    db.commit()


def delete_notification(db: Session, notification_id: str) -> bool:
    notif = get_notification(db, notification_id)
    if not notif: return False
    db.delete(notif); db.commit()
    return True


def get_unread_count(db: Session, user_id: Optional[str] = None):
    q = db.query(models.Notification).filter(models.Notification.is_read == False)
    if user_id:
        q = q.filter(
            (models.Notification.user_id == user_id) | (models.Notification.user_id.is_(None))
        )
    else:
        q = q.filter(models.Notification.user_id.is_(None))
    return q.count()


def seed_demo_notifications(db: Session, user_id: str):
    """Create sample notifications if user has none."""
    existing = db.query(models.Notification).filter(
        (models.Notification.user_id == user_id) | (models.Notification.user_id.is_(None))
    ).first()
    if existing:
        return
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    demos = [
        ("DOCUMENT_EXTRACTED", "Document extraction complete",
         "Your fuel receipt for 'Midnight Run' has been extracted with 92% confidence.", "document", None),
        ("ANOMALY_DETECTED", "Unusual emission spike detected",
         "Travel category in 'Desert Storm' is 3.2x above forecast. Review recommended.", "production", None),
        ("RECOMMENDATION", "New sustainability recommendation",
         "Switch diesel generators to HVO for a projected 18% reduction in Scope 1 emissions.", "production", None),
        ("BUDGET_ALERT", "Carbon budget alert",
         "'Green Horizon' has reached 85% of its carbon budget with 2 shoot days remaining.", "production", None),
        ("SYSTEM", "Welcome to Terra",
         "Get started by creating your first production or uploading activity documents.", None, None),
    ]
    for i, (type_, title, message, entity_type, entity_id) in enumerate(demos):
        notif = models.Notification(
            user_id=user_id,
            type=type_,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False,
            created_at=now - timedelta(hours=i * 2),
        )
        db.add(notif)
    db.commit()


def get_production_summary(db: Session, production_id: str):
    events = get_events_by_production(db, production_id)
    if not events: return None
    total_kg = sum(e.kgco2e for e in events)
    if total_kg == 0: return None
    scope_totals = {}
    for scope in ['SCOPE_1', 'SCOPE_2', 'SCOPE_3']:
        scope_totals[scope] = sum(e.kgco2e for e in events if e.scope == scope)
    cat_totals = {}
    for e in events:
        cat_totals[e.category] = cat_totals.get(e.category, Decimal('0')) + e.kgco2e
    phase_totals = {}
    for e in events:
        phase_totals[e.phase] = phase_totals.get(e.phase, Decimal('0')) + e.kgco2e
    weighted_conf = sum(e.kgco2e * e.confidence_score for e in events) / total_kg
    n = len(events)
    tier1 = sum(1 for e in events if e.confidence_tier == 'TIER_1_DIRECT') / n * 100
    tier2 = sum(1 for e in events if e.confidence_tier == 'TIER_2_BENCHMARK') / n * 100
    tier3 = sum(1 for e in events if e.confidence_tier == 'TIER_3_ML_IMPUTED') / n * 100
    prod = get_production(db, production_id)
    budget_var = None
    if prod and prod.carbon_budget_tco2e and prod.carbon_budget_tco2e > 0:
        actual_tco2e = total_kg / Decimal('1000')
        budget_var = ((actual_tco2e - prod.carbon_budget_tco2e) / prod.carbon_budget_tco2e) * 100
    intensity_hour = None
    intensity_ep = None
    if prod:
        if prod.runtime_min and prod.runtime_min > 0:
            intensity_hour = (total_kg / Decimal('1000')) / (Decimal(str(prod.runtime_min)) / Decimal('60'))
        if prod.episodes and prod.episodes > 0:
            intensity_ep = (total_kg / Decimal('1000')) / Decimal(str(prod.episodes))
    return {
        'production_id': production_id,
        'total_tco2e': round(total_kg / Decimal('1000'), 3),
        'scope_breakdown': {k: round(v / Decimal('1000'), 3) for k, v in scope_totals.items()},
        'category_breakdown': {k: round(v / Decimal('1000'), 3) for k, v in cat_totals.items()},
        'phase_breakdown': {k: round(v / Decimal('1000'), 3) for k, v in phase_totals.items()},
        'overall_confidence': round(weighted_conf, 3),
        'budget_variance_percent': round(budget_var, 1) if budget_var is not None else None,
        'intensity_tco2e_per_hour': round(intensity_hour, 3) if intensity_hour else None,
        'intensity_tco2e_per_episode': round(intensity_ep, 3) if intensity_ep else None,
        'event_count': n,
        'tier_1_percent': tier1,
        'tier_2_percent': tier2,
        'tier_3_percent': tier3,
    }
