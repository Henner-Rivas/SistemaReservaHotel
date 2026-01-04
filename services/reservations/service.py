from __future__ import annotations

from decimal import Decimal
from typing import Dict

from sqlalchemy.orm import Session

from shared.http_client import ServiceClient
from shared.exceptions import NotFoundError, BadRequestError
from services.reservations.repository import (
    create_reservation,
    get_reservation,
    update_reservation_fields,
    update_reservation_status,
)


async def create_reservation_flow(db: Session, payload: Dict, token: str):
    client = ServiceClient()
    bloqueo_id = payload["bloqueo"]["bloqueo_id"]
    reserva = create_reservation(
        db,
        {
            "cliente_id": payload["cliente_id"],
            "hotel_id": payload["hotel_id"],
            "habitacion_id": payload.get("habitacion_id", ""),
            "fecha_inicio": payload["fecha_inicio"],
            "fecha_fin": payload["fecha_fin"],
            "estado": "CREADA",
            "monto_total": Decimal(payload["precio"]["total"]),
            "bloqueo_id": bloqueo_id,
        },
    )
    await client.availability_confirm({"bloqueo_id": bloqueo_id, "reserva_id": reserva.reserva_id}, token)
    update_reservation_status(db, reserva, "CONFIRMADA")
    await client.publish_notification(
        "reserva.creada",
        {
            "reserva_id": reserva.reserva_id,
            "cliente_id": reserva.cliente_id,
            "hotel_id": reserva.hotel_id,
            "monto_total": str(reserva.monto_total),
        },
    )
    return reserva


def modify_reservation(db: Session, reserva_id: str, data: Dict):
    reserva = get_reservation(db, reserva_id)
    if not reserva:
        raise NotFoundError("Reserva no encontrada")
    if reserva.estado not in ("CREADA", "CONFIRMADA"):
        raise BadRequestError("Reserva no modificable en el estado actual")
    return update_reservation_fields(db, reserva, data)


async def cancel_reservation(db: Session, reserva_id: str, token: str):
    reserva = get_reservation(db, reserva_id)
    if not reserva:
        raise NotFoundError("Reserva no encontrada")
    client = ServiceClient()
    # Attempt refund of last approved cargo
    payments = await client.payments_by_reservation(reserva_id, token=token)
    cargos = [t for t in payments.get("transacciones", []) if t.get("tipo") == "cargo" and t.get("estado") == "aprobado"]
    if cargos:
        last = cargos[-1]
        await client.refund_payment(last["transaccion_id"], str(reserva.monto_total), token=token)
    update_reservation_status(db, reserva, "CANCELADA")
    await client.publish_notification("reserva.cancelada", {"reserva_id": reserva_id, "cliente_id": reserva.cliente_id})
    return reserva


def checkin_reservation(db: Session, reserva_id: str):
    reserva = get_reservation(db, reserva_id)
    if not reserva:
        raise NotFoundError("Reserva no encontrada")
    return update_reservation_status(db, reserva, "CHECKIN")


def checkout_reservation(db: Session, reserva_id: str):
    reserva = get_reservation(db, reserva_id)
    if not reserva:
        raise NotFoundError("Reserva no encontrada")
    return update_reservation_status(db, reserva, "CHECKOUT")
