#!/usr/bin/env python3
"""Reset the veille database: removes corrupt DB and creates a fresh one with seed sources."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

db_path = Path(__file__).parent / "veille.db"
wal_path = db_path.with_suffix(".db-wal")
shm_path = db_path.with_suffix(".db-shm")

for f in [db_path, wal_path, shm_path]:
    if f.exists():
        f.unlink()
        print(f"Removed {f.name}")

from app.database import Base, engine, SessionLocal
from app.models import Source

Base.metadata.create_all(bind=engine)
print("Fresh database created.")

from app.main import SEED_SOURCES

db = SessionLocal()
for seed in SEED_SOURCES:
    db.add(Source(**seed))
db.commit()
db.close()
print(f"Seeded {len(SEED_SOURCES)} sources.")
print("\nDone! Start the server with:")
print("  uvicorn app.main:app --reload")
print("  Then open http://127.0.0.1:8000/")
