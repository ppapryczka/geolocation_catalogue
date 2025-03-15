from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints


class GeolocationSchema(BaseModel):
    hostname: str | None = None
    type: Literal["ipv4", "ipv6"]
    continent_code: Literal["AF", "AS", "EU", "NA", "OC", "SA", "AN"]
    continent_name: Literal[
        "Africa",
        "Asia",
        "Europe",
        "North America",
        "Oceania",
        "South America",
        "Antarctica",
    ]
    country_code: Annotated[str, StringConstraints(min_length=2, max_length=2)]
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: str
    latitude: float
    longitude: float


class IpGeolocationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ip: str
    geolocation: GeolocationSchema
