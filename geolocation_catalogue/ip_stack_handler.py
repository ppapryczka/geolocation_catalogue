import logging
from enum import Enum

import requests
from fastapi import HTTPException
from pydantic import ValidationError
from stamina import retry

from geolocation_catalogue.schemas import GeolocationSchema

logging.basicConfig(level=logging.DEBUG)


class IpStackHandlerErrorCode(Enum):
    NOT_FOUND: int = 404


"""
        response_json = {
            "ip": "216.58.209.14",
            "type": "ipv4",
            "continent_code": "NA",
            "continent_name": "North America",
            "country_code": "US",
            "country_name": "United States",
            "region_code": "CA",
            "region_name": "CA",
            "city": "Mountain View",
            "zip": "94041",
            "latitude": 37.38801956176758,
            "longitude": -122.07431030273438,
            "msa": "41940",
            "dma": "807",
            "radius": "None",
            "ip_routing_type": "fixed",
            "connection_type": "ocx",
        }
"""


class IpStackHandler:
    def __init__(self, api_access_key: str) -> None:
        self._api_access_key = api_access_key

    @retry(on=requests.HTTPError)
    def resolve_geolocation(self, ip_address: str) -> None:
        response = requests.get(
            f"https://api.ipstack.com/{ip_address}",
            params={"access_key": self._api_access_key, "fields": "main"},
        )

        response.raise_for_status()
        response_json = response.json()

        print("--------------")
        print(response_json)
        print("--------------")

        # if there is no success key it means success
        success = response_json.get("success", True)
        if not success:
            self._handle_request_error(response_json=response_json)

        try:
            schema = GeolocationSchema(**response_json)
        except ValidationError:
            raise HTTPException(
                status_code=500,
                detail="Internal error related to address's geolocation resolving process.",
            )

        return schema

    def _handle_request_error(self, response_json: dict) -> None:
        unknown_error_exception = HTTPException(
            status_code=500,
            detail="Unknown error during address's geolocation resolving process.",
        )

        error_info = response_json.get("error", None)
        if not error_info:
            raise unknown_error_exception
        error_code = error_info.get("code", None)
        if not error_code:
            raise unknown_error_exception

        match error_code:
            case IpStackHandlerErrorCode.NOT_FOUND:
                raise HTTPException(
                    status_code=404, detail="Geolocation info for address not found."
                )
            case _:
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal error related to address's geolocation resolving process - error code {error_code}",
                )
