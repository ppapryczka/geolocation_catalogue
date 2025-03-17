from enum import Enum

import requests
from fastapi import HTTPException
from pydantic import ValidationError
from stamina import retry

from geolocation_catalogue.schemas import GeolocationSchema


class IpStackHandlerErrorCode(Enum):
    NOT_FOUND: int = 404


class IpStackHandler:
    def __init__(self, api_access_key: str) -> None:
        self._api_access_key = api_access_key

    @retry(on=requests.HTTPError)
    def resolve_geolocation(self, ip_address: str) -> GeolocationSchema:
        response = requests.get(
            f"https://api.ipstack.com/{ip_address}",
            params={"access_key": self._api_access_key, "fields": "main"},
        )

        response.raise_for_status()
        response_json = response.json()

        # if there is no success key ... it means success
        success = response_json.get("success", True)
        if not success:
            self._handle_request_error(response_json=response_json)

        try:
            schema = GeolocationSchema(**response_json)
        except ValidationError:
            raise HTTPException(
                status_code=500,
                detail="Internal error related to address geolocation resolving process.",
            )

        return schema

    def _handle_request_error(self, response_json: dict) -> None:
        unknown_error_exception = HTTPException(
            status_code=500,
            detail="Unknown error during address geolocation resolving process.",
        )

        error_info = response_json.get("error", None)
        if not error_info:
            raise unknown_error_exception
        error_code = error_info.get("code", None)
        if not error_code:
            raise unknown_error_exception
        match error_code:
            case IpStackHandlerErrorCode.NOT_FOUND.value:
                raise HTTPException(
                    status_code=404, detail="Geolocation info for address not found."
                )
            case _:
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal error related to address geolocation resolving process - error code {error_code}",
                )
