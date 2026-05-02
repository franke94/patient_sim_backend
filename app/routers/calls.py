from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Call, Case
from app.models.enums import CallStatusEnum
from app.schemas import CallCreate, CallDetailRead, CallPatchEntries, CallRead, CallSummaryRead

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("", response_model=CallRead, status_code=status.HTTP_201_CREATED)
def create_call(payload: CallCreate, db: Session = Depends(get_db)) -> Call:
    case = db.get(Case, payload.case_id)
    if case is None:
        raise HTTPException(status_code= 404, detail="Case not found")

    call = Call(case_id=case.id, status=CallStatusEnum.RUNNING)
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.get("/{call_id}", response_model=CallDetailRead)
def get_call(call_id: int, db: Session = Depends(get_db)) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.patch("/{call_id}/entries", response_model=CallRead)
def patch_call_entries(
        call_id: int,
        payload: CallPatchEntries,
        db: Session = Depends(get_db),
) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.status != CallStatusEnum.RUNNING:
        raise HTTPException(status_code=404, detail="Call is not running")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(call, field, value)

    db.commit()
    db.refresh(call)
    return call


#Calls abschließen ist eine einzige Aktion, deshlab als post und nicht als patch
@router.post("/{call_id}/complete", response_model=CallRead)
def complete_call(call_id: int, db: Session = Depends(get_db)) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.status == CallStatusEnum.COMPLETED:
        raise HTTPException(status_code=409, detail="Call is already completed")

    call.status = CallStatusEnum.COMPLETED
    call.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(call)
    return call


@router.get("", response_model=list[CallSummaryRead])
def list_calls(db: Session = Depends(get_db)) -> list[CallSummaryRead]:
    #Alle Calls als kleine Summary
    calls = db.query(Call).order_by(Call.started_at.desc()).all()
    return [
        CallSummaryRead(
            id=c.id,
            case_id=c.case_id,
            case_title=c.case.title,
            status=c.status,
            started_at=c.started_at,
            finished_at=c.finished_at
        )
        for c in calls
    ]