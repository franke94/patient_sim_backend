from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseRead

from sqlalchemy import func
from app.models.address_db import AddressDB
from app.simulation.location.matching import simulate_aml

router = APIRouter(prefix="/cases", tags=["cases"])
# prefix cases: alle Endpoints in diesem Router beginnen mit /cases
# tags: Doku-Info


@router.get("", response_model=list[CaseRead])
def list_cases(db: Session = Depends(get_db)) -> list[Case]:
    """Return all cases"""
    return db.query(Case).all()


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)) -> Case:
    """Single case"""
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    return case


@router.post("", status_code=201)
def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    gold = db.query(AddressDB).order_by(func.random()).first()
    if not gold:
        raise HTTPException(status_code=500, detail="Keine Adressen in DB – import_addresses.py laufen lassen")
    aml_lat, aml_lon, aml_acc = simulate_aml(gold.lat, gold.lon)
    new_case = Case(
        **case_data.model_dump(),
        gold_address_id=gold.id, aml_lat=aml_lat, aml_lon=aml_lon, aml_accuracy=aml_acc,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

