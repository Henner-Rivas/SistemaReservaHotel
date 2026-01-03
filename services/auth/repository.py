from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.models import UsuarioDB


def get_user_by_username(db: Session, username: str) -> Optional[UsuarioDB]:
    return db.scalar(select(UsuarioDB).where(UsuarioDB.username == username))


def get_user_by_email(db: Session, email: str) -> Optional[UsuarioDB]:
    return db.scalar(select(UsuarioDB).where(UsuarioDB.email == email))


def create_user(db: Session, email: str, username: str, password_hash: str, nombre_completo: str, telefono: str | None) -> UsuarioDB:
    user = UsuarioDB(
        usuario_id=str(uuid.uuid4())[:8],
        email=email,
        username=username,
        password_hash=password_hash,
        nombre_completo=nombre_completo,
        telefono=telefono,
        rol="cliente",
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user: UsuarioDB):
    from sqlalchemy import func

    user.ultimo_login = func.now()
    db.add(user)
    db.commit()
    db.refresh(user)


def update_user_profile(db: Session, user: UsuarioDB, nombre_completo: str, telefono: str | None) -> UsuarioDB:
    user.nombre_completo = nombre_completo
    user.telefono = telefono
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
