import pandas as pd
from app.database import Base, SessionLocal, engine
from app.models.address_db import AddressDB

"""
Wird gebraucht um die Address csv einmalig in SQLite zu importieren
"""

# Alle Tabellen erstellen (falls noch nicht vorhanden)
Base.metadata.create_all(bind=engine)

df = pd.read_csv("addresses/saarland_addresses_norm.csv")

db = SessionLocal()
try:
    # Sicherheitshalber: bestehende Adressen löschen (Idempotenz)
    db.query(AddressDB).delete()

    batch = []
    for _, row in df.iterrows():
        addr = AddressDB(
            osm_id=int(row["osm_id"]) if pd.notna(row.get("osm_id")) else None,
            city=str(row["city"]) if pd.notna(row.get("city")) else "",
            street=str(row["street"]) if pd.notna(row.get("street")) else "",
            housenumber=str(row["housenumber"]) if pd.notna(row.get("housenumber")) else None,
            postcode=int(row["postcode"]) if pd.notna(row.get("postcode")) else None,
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            city_norm=str(row["city_norm"]) if pd.notna(row.get("city_norm")) else "",
            street_norm=str(row["street_norm"]) if pd.notna(row.get("street_norm")) else "",
            hn_norm=str(row["hn_norm"]) if pd.notna(row.get("hn_norm")) else None,
        )
        batch.append(addr)

        # In 1000er-Batches committen (Performance)
        if len(batch) >= 1000:
            db.bulk_save_objects(batch)
            db.commit()
            batch = []

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    count = db.query(AddressDB).count()
    print(f"Import abgeschlossen: {count} Adressen in DB")
finally:
    db.close()