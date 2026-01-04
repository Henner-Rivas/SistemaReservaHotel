from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MetodoPago(BaseModel):
    tipo: str
    token: str


class CrearReservaRequest(BaseModel):
    cliente_id: str
    hotel_id: str
    tipo_habitacion: str
    fecha_inicio: date
    fecha_fin: date
    servicios_adicionales: Optional[List[str]] = []
    codigo_promocional: Optional[str] = None
    metodo_pago: MetodoPago


class ReservaResponse(BaseModel):
    estado: str
    detalles: Dict[str, Any]
