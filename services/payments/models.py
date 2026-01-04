from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String, func

from shared.database import Base


class TransaccionDB(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True)
    transaccion_id = Column(String(50), unique=True, index=True)
    reserva_id = Column(String(50), index=True, nullable=True)
    cliente_id = Column(String(50), index=True)
    monto = Column(Numeric(10, 2))
    moneda = Column(String(3), default="USD")
    tipo = Column(Enum("cargo", "reembolso"))
    metodo_pago = Column(String(50))
    estado = Column(Enum("pendiente", "aprobado", "rechazado", "reembolsado"))
    codigo_aprobacion = Column(String(50), nullable=True)
    codigo_error = Column(String(10), nullable=True)
    mensaje_error = Column(String(255), nullable=True)
    procesado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
