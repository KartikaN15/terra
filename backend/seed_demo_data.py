"""
Seed Demo Data
Imports productions + activity events from test_data CSVs directly into the database.
Since we're bypassing the calculation engine (data already has kgco2e computed),
we insert rows directly via SQLAlchemy.

Usage:  cd backend && python seed_demo_data.py
"""

import csv
import uuid
import sys
import os
import traceback

# Fix Windows console encoding
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

# Setup path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, engine
from app import models
from app.security import hash_password

TEST_DATA = backend_dir.parent / "test_data"


def parse_datetime(s: str) -> datetime:
    """Parse ISO datetime strings."""
    if not s:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def seed_default_user(db):
    """Create or refresh the default demo user (demo@terra.app / password123)."""
    demo_id = "00000000-0000-0000-0000-000000000001"
    demo_hash = hash_password("password123")
    existing = db.query(models.User).filter(models.User.user_id == demo_id).first()
    if existing:
        existing.hashed_password = demo_hash
        db.commit()
        print(f"  Demo user exists — password reset: demo@terra.app / password123")
        return existing

    user = models.User(
        user_id=demo_id,
        email="demo@terra.app",
        full_name="Demo User",
        hashed_password=demo_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  Created demo user: demo@terra.app / password123 (id={demo_id})")
    return user


def seed_productions(db):
    """Import productions from CSV."""
    csv_path = TEST_DATA / "sample_productions.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return 0

    existing_ids = {str(p.production_id) for p in db.query(models.Production.production_id).all()}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            pid = row["production_id"].strip()
            if pid in existing_ids:
                continue

            # Parse locations as a list
            locations_raw = row.get("locations", "")
            locations = [l.strip() for l in locations_raw.split(";") if l.strip()] if ";" in locations_raw else [locations_raw.strip()] if locations_raw.strip() else []

            prod = models.Production(
                production_id=pid,
                title=row["title"],
                type=row.get("type", "FEATURE"),
                genre=row.get("genre"),
                budget_band=row.get("budget_band"),
                runtime_min=int(row["runtime_min"]) if row.get("runtime_min") else None,
                episodes=int(row["episodes"]) if row.get("episodes") else 1,
                shoot_days=int(row["shoot_days"]) if row.get("shoot_days") else None,
                locations=locations,
                cast_count=int(row["cast_count"]) if row.get("cast_count") else None,
                crew_count=int(row["crew_count"]) if row.get("crew_count") else None,
                vfx_intensity=row.get("vfx_intensity"),
                status=row.get("status", "PRODUCTION"),
                carbon_budget_tco2e=None,
                created_by="00000000-0000-0000-0000-000000000001",
            )
            db.add(prod)
            count += 1

        db.commit()
        print(f"  Seeded {count} productions (skipped {len(existing_ids)} existing)")
        return count


def seed_events(db):
    """Import activity events from CSV with pre-calculated kgco2e."""
    csv_path = TEST_DATA / "sample_activity_events.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return 0

    existing_ids = {str(e.event_id) for e in db.query(models.ActivityEvent.event_id).all()}

    # Get all production IDs so we only insert events for existing productions
    prod_ids = {str(p.production_id) for p in db.query(models.Production.production_id).all()}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        batch = []
        for row in reader:
            eid = row["event_id"].strip()
            pid = row["production_id"].strip()

            if eid in existing_ids:
                continue
            if pid not in prod_ids:
                continue

            event = models.ActivityEvent(
                event_id=eid,
                production_id=pid,
                phase=row.get("phase", "PRODUCTION"),
                scope=row.get("scope", "SCOPE_3"),
                category=row.get("category", ""),
                subcategory=row.get("subcategory", ""),
                value=Decimal(row.get("value", "0")),
                unit=row.get("unit", ""),
                kgco2e=Decimal(row.get("kgco2e", "0")),
                confidence_tier=row.get("confidence_tier", "TIER_2_BENCHMARK"),
                confidence_score=Decimal(row.get("confidence_score", "0.75")),
                source_type=row.get("source_type", "MANUAL_ENTRY"),
                source_reference=row.get("source_reference", ""),
                grid_region=row.get("grid_region", "UK"),
                recorded_at=parse_datetime(row.get("recorded_at", "")),
                recorded_by="00000000-0000-0000-0000-000000000001",
                emission_factor_version="DEFRA_2024",
                calculation_method="activity_based_DEFRA",
            )
            batch.append(event)
            count += 1

            # Batch insert every 200 rows
            if len(batch) >= 200:
                db.add_all(batch)
                db.commit()
                batch = []

        if batch:
            db.add_all(batch)
            db.commit()

        print(f"  Seeded {count} activity events (skipped {len(existing_ids)} existing)")
        return count


def seed_notifications(db, user_id: str):
    """Create a few starter notifications."""
    existing = db.query(models.Notification).count()
    if existing > 0:
        print(f"  Notifications already exist ({existing}), skipping")
        return

    notifs = [
        {
            "type": "SYSTEM",
            "title": "Welcome to Terra 🌱",
            "message": "Your Sustainability Intelligence Platform is ready. Start by exploring your production dashboard.",
        },
        {
            "type": "THRESHOLD_ALERT",
            "title": "High emissions detected",
            "message": "Project 007 (Sci_Fi) has exceeded 5,000 tCO₂e. Consider reviewing transport and energy categories.",
            "entity_type": "production",
            "entity_id": "a9756c65-5631-492d-a7ca-4f7e173f73df",
        },
        {
            "type": "SYSTEM",
            "title": "New recommendations available",
            "message": "3 new reduction recommendations are ready for Project 006 (Horror). Review them in the production detail.",
            "entity_type": "production",
            "entity_id": "f372d94c-70a9-4161-8d86-31359d12a98f",
        },
        {
            "type": "CONFIDENCE_UPDATE",
            "title": "Data quality improved",
            "message": "Project 004 (Drama) confidence score increased from 72% to 85% after invoice verification.",
            "entity_type": "production",
            "entity_id": "e4ba0621-a92b-466d-809e-02451272b921",
        },
    ]

    for n in notifs:
        db.add(models.Notification(
            notification_id=str(uuid.uuid4()),
            user_id=user_id,
            type=n["type"],
            title=n["title"],
            message=n["message"],
            entity_type=n.get("entity_type"),
            entity_id=n.get("entity_id"),
            is_read=False,
        ))
    db.commit()
    print(f"  Seeded {len(notifs)} notifications")


def main():
    print("\n[TERRA] Seeding Demo Data")
    print("=" * 50)

    db = SessionLocal()
    try:
        print("\n1. Creating demo user...")
        user = seed_default_user(db)

        print("\n2. Importing productions...")
        prod_count = seed_productions(db)

        print("\n3. Importing activity events...")
        event_count = seed_events(db)

        print("\n4. Creating notifications...")
        seed_notifications(db, "00000000-0000-0000-0000-000000000001")

        print("\n" + "=" * 50)
        print("[OK] Seeding complete!")

        # Print summary
        total_prods = db.query(models.Production).count()
        total_events = db.query(models.ActivityEvent).count()
        total_factors = db.query(models.EmissionFactor).count()
        total_notifs = db.query(models.Notification).count()
        total_users = db.query(models.User).count()

        print(f"\n--- Database Summary ---")
        print(f"   Productions:      {total_prods}")
        print(f"   Activity Events:  {total_events}")
        print(f"   Emission Factors: {total_factors}")
        print(f"   Users:            {total_users}")
        print(f"   Notifications:    {total_notifs}")
        print()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
