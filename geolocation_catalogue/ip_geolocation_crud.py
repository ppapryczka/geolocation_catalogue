from sqlalchemy import select
from sqlalchemy.orm import Session

from geolocation_catalogue.models import IpGeolocation
from geolocation_catalogue.schemas import GeolocationSchema


class IpGeolocationCRUD:
    @staticmethod
    def create(db: Session, ip: str, geolocation_schema: GeolocationSchema):
        def execute():
            ip_geolocation = IpGeolocation(
                ip=ip, geolocation=geolocation_schema.model_dump()
            )
            db.add(ip_geolocation)
            db.commit()
            return ip_geolocation

        return execute()

    @staticmethod
    def update(
        db: Session,
        ip_geolocation: IpGeolocation,
        geolocation_schema: GeolocationSchema,
    ) -> IpGeolocation:
        def execute():
            ip_geolocation.geolocation = geolocation_schema.model_dump()
            db.commit()
            db.refresh(ip_geolocation)

            return ip_geolocation

        return execute()

    @staticmethod
    def get_by_ip(db: Session, ip: str) -> IpGeolocation | None:
        def execute():
            return db.execute(
                select(IpGeolocation).where(IpGeolocation.ip == ip)
            ).scalar()

        return execute()

    @staticmethod
    def delete(db: Session, ip_geolocation: IpGeolocation) -> None:
        def execute():
            db.delete(ip_geolocation)
            db.commit()

        execute()
