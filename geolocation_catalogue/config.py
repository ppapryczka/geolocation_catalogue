from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    pg_dsn: PostgresDsn

    ip_stack_api_access_key: str | None = None


CONFIG: Config = Config()
