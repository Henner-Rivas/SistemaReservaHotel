from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func

from shared.database import Base


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    nombre_completo = Column(String(255))
    telefono = Column(String(20), nullable=True)
    rol = Column(Enum("admin", "staff", "cliente"), default="cliente")
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, server_default=func.now())
    ultimo_login = Column(DateTime, nullable=True)
