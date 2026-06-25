from sqlalchemy import String, Integer, Float, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from typing import Optional

class AddressDB(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    osm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    city: Mapped[str] = mapped_column(String(255))
    street: Mapped[str] = mapped_column(String(255))
    housenumber: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    postcode: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    city_norm: Mapped[str] = mapped_column(String(255))   # vorberechnete Normalisierung
    street_norm: Mapped[str] = mapped_column(String(255))
    hn_norm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_addr_city_street_hn", "city_norm", "street_norm", "hn_norm"),
    )