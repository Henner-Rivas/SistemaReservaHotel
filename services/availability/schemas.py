from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ConsultaDisponibilidadRequest(BaseModel):
    hotel_id: str
    fecha_inicio: date
    fecha_fin: date
    tipo_habitacion: Optional[str] = None
    numero_huespedes: int = Field(ge=1, le=10)
    precio_maximo: Optional[Decimal] = None


class HabitacionDisponible(BaseModel):
    habitacion_id: str
    numero: str
    tipo: str
    piso: int
    precio_por_noche: Decimal
    precio_total: Decimal
    caracteristicas: List[str]


class DisponibilidadResponse(BaseModel):
    hotel_id: str
    fecha_inicio: date
    fecha_fin: date
    noches: int
    habitaciones: List[HabitacionDisponible]
    total_disponibles: int


class BloquearHabitacionRequest(BaseModel):
    habitacion_id: str
    fecha_inicio: date
    fecha_fin: date
    duracion_minutos: int = 15


class BloqueoResponse(BaseModel):
    bloqueo_id: str
    habitacion_id: str
    expira_en: datetime
    estado: str
