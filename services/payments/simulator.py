from __future__ import annotations

import random
import time
import uuid
from decimal import Decimal


def generar_codigo() -> str:
    return uuid.uuid4().hex[:8].upper()


def simular_procesamiento_pago(monto: Decimal, token: str) -> dict:
    """
    Simula el procesamiento de un pago con reglas de aprobación/rechazo.
    """
    if token == "tok_visa_4242":
        return {"aprobado": True, "codigo": "APR_" + generar_codigo()}

    if token == "tok_rechazado":
        return {"aprobado": False, "codigo": "ERR_001", "mensaje": "Fondos insuficientes"}

    if monto > Decimal("10000.00"):
        return {"aprobado": False, "codigo": "ERR_002", "mensaje": "Monto excede límite"}

    time.sleep(random.uniform(0.1, 0.5))

    if random.random() < 0.1:
        errores = [
            ("ERR_003", "Tarjeta expirada"),
            ("ERR_004", "Transacción sospechosa"),
            ("ERR_005", "Límite diario excedido"),
        ]
        codigo, mensaje = random.choice(errores)
        return {"aprobado": False, "codigo": codigo, "mensaje": mensaje}

    return {"aprobado": True, "codigo": "APR_" + generar_codigo()}
