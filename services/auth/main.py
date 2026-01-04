from __future__ import annotations

import logging
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import Base, engine, get_db
from shared.security import verify_token
from services.auth.models import UsuarioDB
from services.auth.schemas import LoginRequest, RegistroRequest, TokenResponse, UsuarioResponse
from services.auth.service import login_user, register_user


logger = logging.getLogger("auth-service")
app = FastAPI(title="Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Auth service iniciado")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/auth/register", status_code=201)
def register(payload: RegistroRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    user = register_user(db, payload.email, payload.username, payload.password, payload.nombre_completo, payload.telefono)
    return UsuarioResponse(
        usuario_id=user.usuario_id,
        email=user.email,
        username=user.username,
        nombre_completo=user.nombre_completo,
        rol=user.rol,
        activo=user.activo,
    )


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access, refresh = login_user(db, payload.username, payload.password)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=1800)


@app.post("/api/v1/auth/refresh")
def refresh(current_user: dict = Depends(verify_token)) -> TokenResponse:
    # For demo, reissue tokens using current payload
    from services.auth.security import create_access_token, create_refresh_token

    payload = {
        "usuario_id": current_user["usuario_id"],
        "username": current_user["username"],
        "rol": current_user.get("rol", "cliente"),
    }
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=1800)


@app.post("/api/v1/auth/logout")
def logout(current_user: dict = Depends(verify_token)) -> Dict[str, str]:
    # Token invalidation would require a blacklist; omitted in MVP
    return {"message": "logout ok"}


@app.get("/api/v1/auth/me")
def me(current_user: dict = Depends(verify_token)) -> UsuarioResponse:
    return UsuarioResponse(
        usuario_id=current_user["usuario_id"],
        email="",
        username=current_user["username"],
        nombre_completo="",
        rol=current_user.get("rol", "cliente"),
        activo=True,
    )


@app.put("/api/v1/auth/me")
def update_me(payload: RegistroRequest, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> Dict[str, str]:
    # Simplified: only update nombre_completo and telefono for demo
    from services.auth.repository import get_user_by_username, update_user_profile

    user = get_user_by_username(db, current_user["username"])  
    if user:
        update_user_profile(db, user, payload.nombre_completo, payload.telefono)
    return {"message": "perfil actualizado"}
