from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseRead

from sqlalchemy import func
from app.models.address_db import AddressDB
from app.simulation.location.matching import simulate_aml
from app.models import PlausibilityResult, Call
from app.schemas.location import PlausibilityResultRead, ResolveLocationBody
from app.simulation.location.scoring import score_candidates

router = APIRouter(prefix="/calls/{call_id}/location", tags=["location"])

@router.post("/score", response_model=PlausibilityResultRead)
def score_location(call_id: int, body: ResolveLocationBody = ResolveLocationBody(),
                   db: Session = Depends(get_db)):
    call = db.get(Call, call_id)
    if call is None: raise HTTPException(404, "Call not found")
    # address_agent ist optional: ohne ihn gibt es nur AML/Radius-Kandidaten (location_score eigenständig)
    addr = call.address_assessments[-1] if call.address_assessments else None
    matched = addr.matched_addresses if addr else []
    ons = call.onscene_assessments[-1] if call.onscene_assessments else None

    result = score_candidates(
        matched_addresses=matched,
        aml_lat=call.case.aml_lat, aml_lon=call.case.aml_lon, aml_accuracy=call.case.aml_accuracy,
        on_scene_status=(ons.onscene_status if ons else "unknown"),
        on_scene_conf=(ons.confidence if ons else 0.0),
        on_scene_human=body.on_scene_human_result,
    )
    row = PlausibilityResult(call_id=call_id, on_scene_score=result["on_scene_score"],
                             candidates=result["candidates"])
    db.add(row); db.commit(); db.refresh(row)
    return row