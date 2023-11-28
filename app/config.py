from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    AWS_SERVER_PUBLIC_KEY: str
    AWS_SERVER_SECRET_KEY: str


    class Config:
        env_file = ".env"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")