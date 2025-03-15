from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    pg_dsn: PostgresDsn = "postgresql://user:mysecretpassword@localhost:5432/postgres"
    ip_stack_api_access_key: str


CONFIG: Config = Config()
