from __future__ import annotations

import os
from typing import Optional

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Settings(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "hotel_reservations"
    MYSQL_USER: str = "hotel_user"
    MYSQL_PASSWORD: str = "hotel_pass"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


class Base(DeclarativeBase):
    pass


def get_mysql_url() -> str:
    host = settings.MYSQL_HOST
    port = settings.MYSQL_PORT
    db = settings.MYSQL_DB
    user = settings.MYSQL_USER
    pwd = settings.MYSQL_PASSWORD
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"


DATABASE_URL = get_mysql_url()

# Engine and Session
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
