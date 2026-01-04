from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Integer,
    JSON,
    Numeric,
    String,
    func,
)

from shared.database import Base


class HabitacionDB(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True)
    habitacion_id = Column(String(50), unique=True, index=True)
    hotel_id = Column(String(50), index=True)
    numero = Column(String(20))
    tipo = Column(Enum("standard", "deluxe", "suite"))
    piso = Column(Integer)
    capacidad_maxima = Column(Integer)
    precio_base = Column(Numeric(10, 2))
    caracteristicas = Column(JSON)
    activa = Column(Boolean, default=True)


class BloqueoHabitacionDB(Base):
    __tablename__ = "bloqueos_habitacion"

    id = Column(Integer, primary_key=True)
    bloqueo_id = Column(String(50), unique=True, index=True)
    habitacion_id = Column(String(50), index=True)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    tipo = Column(Enum("temporal", "reserva", "mantenimiento"))
    reserva_id = Column(String(50), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    expira_en = Column(DateTime, nullable=True)
    estado = Column(Enum("activo", "expirado", "confirmado"), default="activo")
