from typing import Optional
from enum import Enum
from pydantic import ValidationError

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    AliasChoices
)


class AddressType(str, Enum):
    EMERGENCY_LOCATION = "emergency_location"
    EMERGENCY_LOCATION_PRIMARY = "emergency_location_primary"
    EMERGENCY_LOCATION_ALTERNATIVE = "emergency_location_alternative"
    TRANSPORT_LOCATION = "transport_location"
    CALLER_LOCATION = "caller_location"
    REFERENCE_LOCATION = "reference_location"
    UNKNOWN = "unknown"
    UNCLEAR = "unclear"
    OTHER = "other"
    GOLD = "gold"


class SourceEnum(str, Enum):
    TRANSCRIPT = "transcript"
    ADDRESS_DATABASE = "address_database"
    OSM_LOCATION = "osm_location"
    UNKNOWN = "unknown"
    OTHER = "other"


class Address(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        populate_by_name=True
    )

    osm_id: Optional[int] = None
    city: Optional[str] = None
    postcode: Optional[int] = None
    street: Optional[str] = None

    housenumber: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "housenumber",
            "house_number"
        )
    )

    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)

    gps_distance: Optional[float] = None

    type: AddressType = AddressType.UNKNOWN

    special_notes: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "special_notes",
            "details"
        )
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1
    )

    source: SourceEnum = SourceEnum.UNKNOWN

    fuzzy_mode: Optional[dict] = None

class AddressResult(BaseModel):
    addresses: list[Address] = []