from pydantic_settings import BaseSettings
from pathlib import Path

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
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str


    class Config:
        env_file = Path("/home/lex/something-backend/.env")


settings = Settings(_env_file=Path("/home/lex/something-backend/.env"), _env_file_encoding="utf-8")