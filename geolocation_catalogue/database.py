from typing import Iterator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from geolocation_catalogue.config import CONFIG

ENGINE = create_engine(str(CONFIG.pg_dsn), pool_pre_ping=True)

SESSION_MAKER = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def get_db(request: Request) -> Iterator[Session]:
    db = SESSION_MAKER()
    try:
        yield db
    finally:
        db.close()
