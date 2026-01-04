from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        usuario_id = payload.get("usuario_id")
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
