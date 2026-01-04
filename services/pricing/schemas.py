from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CalcularPrecioRequest(BaseModel):
    hotel_id: str
    tipo_habitacion: str
    fecha_inicio: date
    fecha_fin: date
    servicios_adicionales: Optional[List[str]] = []
    codigo_promocional: Optional[str] = None


class DetallesPrecio(BaseModel):
    subtotal: Decimal
    impuestos: Decimal
    servicios_adicionales: Decimal
    descuentos: Decimal
    total: Decimal
    moneda: str = "USD"
    desglose: list


class ValidarCuponRequest(BaseModel):
    codigo: str
    monto: Decimal
    fecha_reserva: date
    noches: int


class ValidarCuponResponse(BaseModel):
    codigo: str
    valido: bool
    descuento: Decimal
    mensaje: str
