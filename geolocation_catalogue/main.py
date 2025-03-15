from socket import gethostbyname
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import AfterValidator
from sqlalchemy import select
from sqlalchemy.orm import Session

from geolocation_catalogue.config import CONFIG
from geolocation_catalogue.database import get_db
from geolocation_catalogue.ip_stack_handler import IpStackHandler
from geolocation_catalogue.models import IpGeolocation
from geolocation_catalogue.schemas import (GeolocationSchema,
                                           IpGeolocationSchema)

DESCRIPTION: str = "API which stores geolocation info of IP addresses and hostnames."

app = FastAPI(description=DESCRIPTION)


def is_valid_address(address: str) -> str:
    print("is_valid_address", address)
    return address


@app.get("/")
def root():
    return {"description": DESCRIPTION}


@app.get("/address", response_model=IpGeolocationSchema)
def get_address_geolocation(
    address: Annotated[str, AfterValidator(is_valid_address)],
    db: Session = Depends(get_db),
) -> IpGeolocationSchema:
    ip = gethostbyname(address)

    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == ip)
    ).scalar()
    if ip_geolocation:
        return ip_geolocation

    ip_stack_handler = IpStackHandler(api_access_key=CONFIG.ip_stack_api_access_key)
    geolocation = ip_stack_handler.resolve_geolocation(ip_address=ip)
    ip_geolocation = IpGeolocation(ip=ip, geolocation=geolocation.dict())

    db.add(ip_geolocation)
    db.commit()
    db.refresh(ip_geolocation)

    return ip_geolocation


@app.put("/address")
def put_address_geolocation(
    address: Annotated[str, AfterValidator(is_valid_address)],
    geolocation: GeolocationSchema,
    db=Depends(get_db),
):
    ip = gethostbyname(address)
    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == ip)
    ).scalar()
    if ip_geolocation:
        ip_geolocation.geolocation = geolocation.dict()
    else:
        ip_geolocation = IpGeolocation(ip=ip, geolocation=geolocation.dict())
        db.add(ip_geolocation)

    db.commit()
    db.refresh(ip_geolocation)
    return ip_geolocation


@app.delete("/address")
def delete_address_geolocation(
    address: Annotated[str, AfterValidator(is_valid_address)],
    db: Session = Depends(get_db),
):
    ip = gethostbyname(address)
    ip_geolocation = db.execute(
        select(IpGeolocation).where(IpGeolocation.ip == ip)
    ).scalar()
    if not ip_geolocation:
        raise HTTPException(
            status_code=404, detail="Geolocation for given address not found."
        )

    ip_geolocation = ip_geolocation[0]
    db.delete(ip_geolocation)
    db.commit()
    return Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
