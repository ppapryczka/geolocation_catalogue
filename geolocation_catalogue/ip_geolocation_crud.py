from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from stamina import retry

from geolocation_catalogue.models import IpGeolocation
from geolocation_catalogue.schemas import GeolocationSchema


class IpGeolocationCRUD:
    @retry(on=SQLAlchemyError, attempts=5, timeout=3)
    @staticmethod
    def create(db: Session, ip: str, geolocation_schema: GeolocationSchema):
        ip_geolocation = IpGeolocation(
            ip=ip, geolocation=geolocation_schema.model_dump()
        )
        db.add(ip_geolocation)
        db.commit()
        return ip_geolocation

    @retry(on=SQLAlchemyError, attempts=5, timeout=3)
    @staticmethod
    def update(
        db: Session,
        ip_geolocation: IpGeolocation,
        geolocation_schema: GeolocationSchema,
    ) -> IpGeolocation:
        ip_geolocation.geolocation = geolocation_schema.model_dump()
        db.commit()
        db.refresh(ip_geolocation)

        return ip_geolocation

    @retry(on=SQLAlchemyError, attempts=5, timeout=3)
    @staticmethod
    def get_by_ip(db: Session, ip: str) -> IpGeolocation | None:
        return db.execute(select(IpGeolocation).where(IpGeolocation.ip == ip)).scalar()

    @retry(on=SQLAlchemyError, attempts=5, timeout=3)
    @staticmethod
    def delete(db: Session, ip_geolocation: IpGeolocation) -> None:
        db.delete(ip_geolocation)
        db.commit()
