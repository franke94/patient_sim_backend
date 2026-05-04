from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, func, ForeignKey, CheckConstraint, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.call import Call

from app.database import Base
from app.models.enums import QualificationEnum


class CallFeedback(Base):
    """ 1:1 Beziehung zu Call, alle Felder sind nullable"""
    __tablename__ = "call_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)

    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id"), unique=True, index=True
    )
    call: Mapped["Call"] = relationship(back_populates="feedback")

    realism_score: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint(
            "realism_score IS NULL OR realism_score BETWEEN 1 AND 5",
            name="realism_score_range",
        ),
        nullable=True,
    )

    ai_assessment_score: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint(
            "ai_assessment_score IS NULL OR realism_score BETWEEN 1 AND 5",
            name="ai_assessment_score_score_range",
        ),
        nullable=True,
    )

    ai_collaboration_score: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint(
            "ai_collaboration_score IS NULL OR realism_score BETWEEN 1 AND 5",
            name="ai_collaboration_score_range",
        ),
        nullable=True,
    )

    #Qualifikation
    qualification: Mapped[QualificationEnum | None] = mapped_column(
        SQLEnum(QualificationEnum), nullable=True
    )

    #Leitstelle
    works_in_dispatch: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    #Freitext
    feedback_text: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime]=mapped_column(
        DateTime, server_default=func.now()
    )
