import pytest
from geolocation_catalogue.config import CONFIG
from geolocation_catalogue.main import get_db, app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from geolocation_catalogue.models import Base, IpGeolocation
from geolocation_catalogue.schemas import GeolocationSchema
from sqlalchemy import select


IP_STACK_RESPONSES: dict[str, dict] = {
    "216.58.209.14": {
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
}

TEST_IP_STACK_API_ACCESS_KEY: str = "test"

TEST_ENGINE = create_engine(str(CONFIG.pg_dsn))
# Note! pytest-env ensures that we are using tests database.
# Test pg_dsn value is set in section tool.pytest.ini_options of pyproject.toml file.

TEST_SESSION_MAKER = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    try:
        db = TEST_SESSION_MAKER()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)


@pytest.fixture()
def test_app() -> TestClient:
    with TestClient(app) as c:
        app.dependency_overrides[get_db] = override_get_db
        yield c


@pytest.fixture()
def test_app_ip_stack_on() -> TestClient:
    with TestClient(app) as c:
        CONFIG.ip_stack_api_access_key = "test"
        app.dependency_overrides[get_db] = override_get_db
        yield c
        CONFIG.ip_stack_api_access_key = None


def insert_into_database(ip: str, geolocation: dict) -> None:
    try:
        db = next(override_get_db())
        geolocation_schema = GeolocationSchema(**geolocation)
        ip_geolocation = IpGeolocation(
            ip=ip, geolocation=geolocation_schema.model_dump()
        )
        db.add(ip_geolocation)
        db.commit()
    finally:
        db.close()


def get_ip_geolocation_from_db(ip: str) -> IpGeolocation:
    try:
        db = next(override_get_db())
        res = db.execute(select(IpGeolocation).where(IpGeolocation.ip == ip)).scalar()
    finally:
        db.close()

    return res
