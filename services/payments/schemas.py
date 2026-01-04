from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MetodoPago(BaseModel):
    tipo: str = Field(pattern=r"^(tarjeta_credito|tarjeta_debito|paypal)$")
    token: str = Field(min_length=10)
    titular: Optional[str] = None


class ProcesarPagoRequest(BaseModel):
    cliente_id: str
    reserva_id: Optional[str] = None
    monto: Decimal = Field(gt=0)
    moneda: str = "USD"
    metodo_pago: MetodoPago
    descripcion: Optional[str] = None


class TransaccionResponse(BaseModel):
    transaccion_id: str
    estado: str
    monto: Decimal
    codigo_aprobacion: Optional[str]
    mensaje: str
    procesado_en: datetime


class ReembolsarRequest(BaseModel):
    transaccion_id: str
    monto: Decimal
    razon: Optional[str] = None
