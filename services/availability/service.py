from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from services.availability.models import HabitacionDB
from services.availability.repository import (
    confirm_block,
    create_block,
    expire_block,
    get_block,
    list_active_blocks_in_range,
    list_rooms_by_hotel,
    overlapping_blocks,
)
from shared.exceptions import BadRequestError, NotFoundError


def nights_between(start: date, end: date) -> int:
    return (end - start).days


def search_availability(db: Session, hotel_id: str, fecha_inicio: date, fecha_fin: date, tipo_habitacion: str | None, precio_maximo: Decimal | None) -> List[dict]:
    rooms = list_rooms_by_hotel(db, hotel_id, tipo_habitacion)
    blocks = list_active_blocks_in_range(db, hotel_id, fecha_inicio, fecha_fin)
    blocked_ids = {b.habitacion_id for b in blocks}
    noches = nights_between(fecha_inicio, fecha_fin)
    result = []
    for r in rooms:
        if r.habitacion_id in blocked_ids:
            continue
        precio_noche = Decimal(r.precio_base)
        precio_total = (precio_noche * noches).quantize(Decimal("0.01"))
        if precio_maximo and precio_noche > precio_maximo:
            continue
        result.append(
            {
                "habitacion_id": r.habitacion_id,
                "numero": r.numero,
                "tipo": r.tipo,
                "piso": r.piso,
                "precio_por_noche": str(precio_noche),
                "precio_total": str(precio_total),
                "caracteristicas": r.caracteristicas or [],
            }
        )
    return result


def block_room(db: Session, habitacion_id: str, fecha_inicio: date, fecha_fin: date, duracion_minutos: int) -> dict:
    if overlapping_blocks(db, habitacion_id, fecha_inicio, fecha_fin):
        raise BadRequestError("La habitación ya tiene un bloqueo activo en ese rango")
    expira = datetime.utcnow() + timedelta(minutes=duracion_minutos)
    bloqueo = create_block(db, habitacion_id, fecha_inicio, fecha_fin, expira, "temporal")
    return {
        "bloqueo_id": bloqueo.bloqueo_id,
        "habitacion_id": bloqueo.habitacion_id,
        "expira_en": bloqueo.expira_en,
        "estado": bloqueo.estado,
    }


def release_block(db: Session, bloqueo_id: str):
    bloqueo = get_block(db, bloqueo_id)
    if not bloqueo:
        raise NotFoundError("Bloqueo no encontrado")
    expire_block(db, bloqueo)


def confirm_block_reservation(db: Session, bloqueo_id: str, reserva_id: str) -> dict:
    bloqueo = get_block(db, bloqueo_id)
    if not bloqueo:
        raise NotFoundError("Bloqueo no encontrado")
    if bloqueo.estado != "activo":
        raise BadRequestError("Bloqueo no activo")
    bloqueo = confirm_block(db, bloqueo, reserva_id)
    return {
        "bloqueo_id": bloqueo.bloqueo_id,
        "habitacion_id": bloqueo.habitacion_id,
        "estado": bloqueo.estado,
        "reserva_id": bloqueo.reserva_id,
    }


def cleanup_expired_blocks(db: Session):
    from sqlalchemy import select
    from services.availability.models import BloqueoHabitacionDB

    now = datetime.utcnow()
    stmt = select(BloqueoHabitacionDB).where(
        BloqueoHabitacionDB.estado == "activo",
        BloqueoHabitacionDB.expira_en.is_not(None),
        BloqueoHabitacionDB.expira_en < now,
    )
    for bloqueo in db.scalars(stmt):
        expire_block(db, bloqueo)
