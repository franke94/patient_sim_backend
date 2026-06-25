from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.address_db import AddressDB
from app.simulation.location.matching_rich import normalize_text, normalize_hn

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("/cities")
def list_cities(q: str = "", limit: int = 20, db: Session = Depends(get_db)) -> list[str]:
    qn = normalize_text(q)
    stmt = (select(AddressDB.city)
            .where(AddressDB.city_norm.like(f"{qn}%"))
            .distinct().order_by(AddressDB.city).limit(limit))
    return [r[0] for r in db.execute(stmt).all()]


@router.get("/streets")
def list_streets(city: str, q: str = "", limit: int = 20, db: Session = Depends(get_db)) -> list[str]:
    cn, qn = normalize_text(city), normalize_text(q)
    stmt = (select(AddressDB.street)
            .where(AddressDB.city_norm == cn, AddressDB.street_norm.like(f"{qn}%"))
            .distinct().order_by(AddressDB.street).limit(limit))
    return [r[0] for r in db.execute(stmt).all()]


@router.get("/housenumbers")
def list_housenumbers(city: str, street: str, q: str = "", limit: int = 20,
                      db: Session = Depends(get_db)) -> list[str]:
    cn, sn, qn = normalize_text(city), normalize_text(street), normalize_hn(q)
    stmt = (select(AddressDB.housenumber)
            .where(AddressDB.city_norm == cn, AddressDB.street_norm == sn,
                   AddressDB.hn_norm.like(f"{qn}%"))
            .distinct().order_by(AddressDB.housenumber).limit(limit))
    return [r[0] for r in db.execute(stmt).all() if r[0] is not None]