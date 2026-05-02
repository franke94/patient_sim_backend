from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AgentRun, Call
from app.models.enums import AgentRunStatusEnum, AgentTypeEnum
from app.schemas import AgentRunRead
from app.simulation.agents import get_agent_class

router = APIRouter(prefix="/calls/{call_id}/agents", tags=["agents"])

@router.post("/{agent_type}", response_model=AgentRunRead, status_code=status.HTTP_200_OK)
def trigger_agent(
        call_id = int,
        agent_type = AgentTypeEnum,
        db: Session = Depends(get_db)
    ):
    """Initierung eines Agent Runs """
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")

    try:
        agent_cls = get_agent_class(agent_type)
    except KeyError as exc:
        raise HTTPException(status_code=501, detail=str(exc))

    agent = agent_cls(call, db)
    run = agent.run()
    db.commit()
    db.refresh(run)
    return run
