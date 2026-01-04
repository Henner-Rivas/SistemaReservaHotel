from __future__ import annotations

from datetime import date
from sqlalchemy import Column, Date, DateTime, Enum, Integer, String, func

from shared.database import Base


class ClienteDB(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(50), unique=True, index=True)
    usuario_id = Column(String(50), index=True, nullable=True)
    nombre_completo = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    telefono = Column(String(20))
    fecha_nacimiento = Column(Date, nullable=True)
    direccion = Column(String(500), nullable=True)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    documento_identidad = Column(String(50), nullable=True)
    tipo_documento = Column(Enum("dni", "pasaporte", "cedula"), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, onupdate=func.now())
