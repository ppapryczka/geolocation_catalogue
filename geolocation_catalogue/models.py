from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


class IpGeolocation(Base):
    __tablename__ = "ip_geolocation"

    ip: Mapped[str] = mapped_column(primary_key=True)
    geolocation: Mapped[dict[str, Any]] = mapped_column(nullable=False)
