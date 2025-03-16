from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import AfterValidator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from geolocation_catalogue.address_validator import validate_address
from geolocation_catalogue.config import CONFIG
from geolocation_catalogue.database import get_db
from geolocation_catalogue.ip_geolocation_crud import IpGeolocationCRUD
from geolocation_catalogue.ip_stack_handler import IpStackHandler
from geolocation_catalogue.schemas import GeolocationSchema, IpGeolocationSchema

DESCRIPTION: str = "API which stores geolocation info of IP addresses and hostnames."

app = FastAPI(description=DESCRIPTION)


@app.get("/")
def root():
    return {"description": DESCRIPTION}


@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    # TODO - we should send error to sentry

    if isinstance(exc, SQLAlchemyError):
        return Response(
            status_code=500, content="Unknown database error during query execution."
        )

    raise Response(status_code=500, content="Unknown error during query execution.")


@app.get("/address", response_model=IpGeolocationSchema)
def get_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    db: Session = Depends(get_db),
) -> IpGeolocationSchema:
    ip_geolocation = IpGeolocationCRUD.get_by_ip(db, address)

    if ip_geolocation:
        return ip_geolocation

    if not ip_geolocation and not CONFIG.ip_stack_api_access_key:
        raise HTTPException(
            status_code=404, detail="Geolocation for address not found."
        )

    ip_stack_handler = IpStackHandler(api_access_key=CONFIG.ip_stack_api_access_key)
    geolocation_schema = ip_stack_handler.resolve_geolocation(ip_address=address)

    return IpGeolocationCRUD.create(db, address, geolocation_schema)


@app.put("/address", response_model=IpGeolocationSchema)
def put_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    geolocation: GeolocationSchema,
    db=Depends(get_db),
) -> IpGeolocationSchema:
    ip_geolocation = IpGeolocationCRUD.get_by_ip(db, address)

    if ip_geolocation:
        return IpGeolocationCRUD.update(db, ip_geolocation, geolocation)
    else:
        return IpGeolocationCRUD.create(db, address, geolocation)


@app.delete("/address")
def delete_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    db: Session = Depends(get_db),
) -> Response:
    ip_geolocation = IpGeolocationCRUD.get_by_ip(db, address)

    if not ip_geolocation:
        raise HTTPException(
            status_code=404, detail="Geolocation for given address not found."
        )

    IpGeolocationCRUD.delete(db, ip_geolocation)

    return Response(status_code=204)
