"""
Seed emission factors from CSV into PostgreSQL.
Run: python seed_emission_factors.py
"""
import os
import csv
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent))
from app.database import Base
from app.models import EmissionFactor

DB_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/sustainability")
ENGINE = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
Session = sessionmaker(bind=ENGINE)


def seed():
    Base.metadata.create_all(bind=ENGINE)
    db = Session()

    csv_path = Path(__file__).parent.parent / "test_data" / "sample_emission_factors.csv"
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return

    count = 0
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip if already exists
            exists = db.query(EmissionFactor).filter(
                EmissionFactor.standard == row["standard"],
                EmissionFactor.category == row["category"],
                EmissionFactor.subcategory == row["subcategory"],
                EmissionFactor.region == row["region"],
                EmissionFactor.version == row["version"],
            ).first()
            if exists:
                continue

            db.add(EmissionFactor(
                standard=row["standard"],
                category=row["category"],
                subcategory=row["subcategory"],
                activity_type=row["activity_type"],
                factor_value=row["factor_value"],
                unit=row["unit"],
                scope=row["scope"],
                region=row["region"],
                country_code=row.get("country_code"),
                grid_intensity_g_co2_kwh=row.get("grid_intensity_g_co2_kwh") or None,
                valid_from=datetime.strptime(row["valid_from"], "%Y-%m-%d"),
                version=row["version"],
                description=f"{row['standard']} factor for {row['subcategory']}",
                radiative_forcing_multiplier=row.get("radiative_forcing_multiplier") or "1.0",
                wtt_factor=row.get("wtt_factor") or None,
                is_active=True,
            ))
            count += 1

    db.commit()
    db.close()
    print(f"Seeded {count} emission factors.")


if __name__ == "__main__":
    seed()
