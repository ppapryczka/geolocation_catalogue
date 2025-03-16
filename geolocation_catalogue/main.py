from socket import gethostbyname
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import AfterValidator
from sqlalchemy import select
from sqlalchemy.orm import Session

from geolocation_catalogue.address_validator import validate_address
from geolocation_catalogue.config import CONFIG
from geolocation_catalogue.database import get_db
from geolocation_catalogue.ip_stack_handler import IpStackHandler
from geolocation_catalogue.models import IpGeolocation
from geolocation_catalogue.schemas import GeolocationSchema, IpGeolocationSchema

DESCRIPTION: str = "API which stores geolocation info of IP addresses and hostnames."

app = FastAPI(description=DESCRIPTION)


@app.get("/")
def root():
    return {"description": DESCRIPTION}


@app.get("/address", response_model=IpGeolocationSchema)
def get_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    db: Session = Depends(get_db),
) -> IpGeolocationSchema:
    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == address)
    ).scalar()

    if ip_geolocation:
        return ip_geolocation

    if not ip_geolocation and not CONFIG.ip_stack_api_access_key:
        raise HTTPException(
            status_code=404, detail="Geolocation for address not found."
        )

    ip_stack_handler = IpStackHandler(api_access_key=CONFIG.ip_stack_api_access_key)
    geolocation = ip_stack_handler.resolve_geolocation(ip_address=address)
    ip_geolocation = IpGeolocation(ip=address, geolocation=geolocation.model_dump())

    db.add(ip_geolocation)
    db.commit()
    db.refresh(ip_geolocation)

    return ip_geolocation


@app.put("/address", response_model=IpGeolocationSchema)
def put_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    geolocation: GeolocationSchema,
    db=Depends(get_db),
):
    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == address)
    ).scalar()

    if ip_geolocation:
        ip_geolocation.geolocation = geolocation.model_dump()
    else:
        ip_geolocation = IpGeolocation(ip=address, geolocation=geolocation.model_dump())
        db.add(ip_geolocation)

    db.commit()
    db.refresh(ip_geolocation)
    return ip_geolocation


@app.delete("/address")
def delete_address_geolocation(
    address: Annotated[str, AfterValidator(validate_address)],
    db: Session = Depends(get_db),
):
    ip = gethostbyname(address)
    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == address)
    ).scalar()
    if not ip_geolocation:
        raise HTTPException(
            status_code=404, detail="Geolocation for given address not found."
        )

    db.delete(ip_geolocation)
    db.commit()
    return Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
