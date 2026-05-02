from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Call, ChatMessage
from app.models.enums import CallStatusEnum, MessageRoleEnum
from app.schemas import ChatMessageCreate, ChatMessageRead
from app.simulation.caller import run_caller_turn
from app.simulation.llm import LLMError

"""
Spiegelt den Chat-Turn vollständig wieder:
Im Request gilt:
- User Message (Calltaker) wird gespeichert
- LLM Aufruf generiert die Antwort des Notrufers
- Agent-Message wird gespeichert
- Client bekommt beide Messages zurück
"""

router = APIRouter(prefix="/calls/{call_id}/messages", tags=["messages"])

@router.post(
    "",
    response_model=list[ChatMessageRead],
    status_code=status.HTTP_201_CREATED,
)
def post_message(
        call_id: int,
        payload: ChatMessageCreate,
        db: Session = Depends(get_db),
) -> list[ChatMessage]:
    """Append a user message and gets the caller reply"""
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.status != CallStatusEnum.RUNNING:
        raise HTTPException(status_code=409, detail="Call is not running")

    last_order = max((m.order_index for m in call.messages), default=-1)
    user_msg=ChatMessage(
        call=call,
        role=MessageRoleEnum.USER,
        content=payload.content,
        order_index=last_order + 1,
    )
    db.add(user_msg)
    db.flush() # user_msg gets ID + appears in call.messages for run_caller_turn
    #Flush schiebt Änderungen ans DB Backend ohne zu kommitten, damit lässt sich die message order korrekt ermitteln
    try:
        caller_msg = run_caller_turn(call, db)
    except LLMError as exc:
        db.rollback() #User Message verwerfen
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY, detail=f"LLM provider error: {exc}"
        )
    db.commit()
    db.refresh(user_msg)
    db.refresh(caller_msg)
    return [user_msg, caller_msg]