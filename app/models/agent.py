from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AgentTypeEnum, AgentRunStatusEnum

if TYPE_CHECKING:
    from app.models.call import Call
    from app.models.assessment import ABCDEAssessment, InjuryAssessment

class AgentRun(Base):
    """Einzelne Execution des AI Agents für einen spezifischen call. Trackt die Metadaten und LLM output"""
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))

    agent_type: Mapped[AgentTypeEnum] = mapped_column(SQLEnum(AgentTypeEnum))
    status: Mapped[AgentRunStatusEnum] = mapped_column(
        SQLEnum(AgentRunStatusEnum),
        default=AgentRunStatusEnum.PENDING
    )

    input_snapshot: Mapped[dict | None] = mapped_column(JSON)
    raw_output: Mapped[dict | None] = mapped_column(JSON)

    error_message: Mapped[str | None] = mapped_column(Text)
    tokens_used: Mapped[int| None]= mapped_column()

    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)

    call: Mapped["Call"] = relationship(back_populates="agent_runs")
    abcde_assessments: Mapped[list["ABCDEAssessment"]] = relationship(back_populates="agent_run")
    injury_assessments: Mapped[list["InjuryAssessment"]] = relationship(back_populates="agent_run")