from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, func, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

#TYPE_CHECKING verhindert zirkuläre abhängigkeiten während der Laufzeit (da während der Ausführung TYPE_CHECKING = False, und erst wenn aufgerufen als Typechecker dann True
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.assessment import ABCDEAssessment, InjuryAssessment
    from app.models.chat import ChatMessage
    from app.models.agent import AgentRun
    from app.models.feedback import CallFeedback

from app.database import Base
from app.models.enums import CallStatusEnum, LanguageEnum


# Hinweis: text ist nicht längenbeschränkt, String(255) kann 255 char
# func.now() setzt über die DB den Timestamp und ist damit konsistenter


class Call(Base):
    """Call Template: Wird in der laufenden Simulation erstellt, enthält die Ergebnisse des USer Tests"""
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    case: Mapped["Case"] = relationship(back_populates="calls")
    # Verweis auf Calls, da keine List sondern nur ein eigener Case ist 1:n umgesetzt

    status: Mapped[CallStatusEnum] = mapped_column(
        SQLEnum(CallStatusEnum),
        default=CallStatusEnum.RUNNING
    )
    language: Mapped[LanguageEnum] = mapped_column(SQLEnum(LanguageEnum), server_default=LanguageEnum.DE.value, default=LanguageEnum.DE)
    started_at: Mapped[datetime]= mapped_column(
        DateTime, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)

    address_entered: Mapped[str | None] = mapped_column(String(500))
    patient_name_entered: Mapped[str | None] = mapped_column(String(255))
    caller_name_entered: Mapped[str | None] = mapped_column(String(255))

    #Forward Reference auf die assessments
    abcde_assessments: Mapped[list["ABCDEAssessment"]] = relationship(back_populates="call")
    injury_assessments: Mapped[list["InjuryAssessment"]] = relationship(back_populates="call")

    #Reference auf einzelne Messages
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="call",
        order_by="ChatMessage.order_index"
    )

    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates= "call")

    feedback: Mapped["CallFeedback | None"] = relationship(
        back_populates="call",uselist=False
    )
