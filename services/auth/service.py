from __future__ import annotations

from typing import Tuple

from sqlalchemy.orm import Session

from services.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_password_rules,
    verify_password,
)
from services.auth.repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_last_login,
    update_user_profile,
)
from shared.exceptions import BadRequestError, ConflictError


def register_user(db: Session, email: str, username: str, password: str, nombre_completo: str, telefono: str | None):
    if not validate_password_rules(password):
        raise BadRequestError("La contraseña no cumple las reglas (8+, 1 mayúscula, 1 número)")
    if get_user_by_email(db, email):
        raise ConflictError("Email ya registrado")
    if get_user_by_username(db, username):
        raise ConflictError("Username ya registrado")
    return create_user(db, email, username, hash_password(password), nombre_completo, telefono)


def login_user(db: Session, username: str, password: str) -> Tuple[str, str]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise BadRequestError("Credenciales inválidas")
    update_last_login(db, user)
    payload = {
        "usuario_id": user.usuario_id,
        "username": user.username,
        "rol": user.rol,
    }
    return create_access_token(payload), create_refresh_token(payload)
