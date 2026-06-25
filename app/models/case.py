from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
from app.models.enums import LanguageEnum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import AMLAccuracyEnum
from app.models.address_db import AddressDB

if TYPE_CHECKING:
    from app.models.call import Call
    from app.models.assessment import ABCDEAssessment, InjuryAssessment

from app.database import Base


# Hinweis: text ist nicht längenbeschränkt, String(255) kann 255 char
# func.now() setzt über die DB den Timestamp und ist damit konsistenter


class Case(Base):
    """Case Template: Wir vorgegeben, enthält den Prompt und die Truth-Werte"""
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    case_description: Mapped[str] = mapped_column(Text)
    gold_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    aml_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aml_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aml_accuracy: Mapped[Optional[AMLAccuracyEnum]] = mapped_column(
        SQLEnum(AMLAccuracyEnum), nullable=True
    )
    patient_name: Mapped[str] = mapped_column(String(255))
    caller_name: Mapped[str] = mapped_column(String(255))
    caller_prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())

    # Forward Reference auf Call, list zeigt das 1:n
    calls: Mapped[list["Call"]] = relationship(back_populates="case")

    #Forward Reference auf die assessments,
    abcde_assessments: Mapped[list["ABCDEAssessment"]] = relationship(back_populates="case")
    injury_assessments: Mapped[list["InjuryAssessment"]] = relationship(back_populates="case")

    language: Mapped[LanguageEnum] = mapped_column(SQLEnum(LanguageEnum), server_default=LanguageEnum.DE.value, default=LanguageEnum.DE)

    #Neue Relationship
    gold_address: Mapped["AddressDB"] = relationship()