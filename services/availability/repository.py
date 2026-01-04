from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from services.availability.models import BloqueoHabitacionDB, HabitacionDB


def list_rooms_by_hotel(db: Session, hotel_id: str, tipo: str | None = None) -> List[HabitacionDB]:
    stmt = select(HabitacionDB).where(HabitacionDB.hotel_id == hotel_id, HabitacionDB.activa == True)
    if tipo:
        stmt = stmt.where(HabitacionDB.tipo == tipo)
    return list(db.scalars(stmt))


def overlapping_blocks(db: Session, habitacion_id: str, inicio: date, fin: date) -> List[BloqueoHabitacionDB]:
    # Overlap if (start <= existing.fin) and (end >= existing.inicio)
    stmt = select(BloqueoHabitacionDB).where(
        BloqueoHabitacionDB.habitacion_id == habitacion_id,
        BloqueoHabitacionDB.estado == "activo",
        and_(inicio <= BloqueoHabitacionDB.fecha_fin, fin >= BloqueoHabitacionDB.fecha_inicio),
    )
    return list(db.scalars(stmt))


def list_active_blocks_in_range(db: Session, hotel_id: str, inicio: date, fin: date) -> List[BloqueoHabitacionDB]:
    rooms_stmt = select(HabitacionDB.habitacion_id).where(HabitacionDB.hotel_id == hotel_id)
    stmt = select(BloqueoHabitacionDB).where(
        BloqueoHabitacionDB.habitacion_id.in_(rooms_stmt),
        BloqueoHabitacionDB.estado == "activo",
        and_(inicio <= BloqueoHabitacionDB.fecha_fin, fin >= BloqueoHabitacionDB.fecha_inicio),
    )
    return list(db.scalars(stmt))


def create_block(db: Session, habitacion_id: str, inicio: date, fin: date, expira_en: Optional[datetime], tipo: str = "temporal", reserva_id: Optional[str] = None) -> BloqueoHabitacionDB:
    bloqueo = BloqueoHabitacionDB(
        bloqueo_id=str(uuid.uuid4())[:8],
        habitacion_id=habitacion_id,
        fecha_inicio=inicio,
        fecha_fin=fin,
        tipo=tipo,
        reserva_id=reserva_id,
        expira_en=expira_en,
        estado="activo",
    )
    db.add(bloqueo)
    db.commit()
    db.refresh(bloqueo)
    return bloqueo


def get_block(db: Session, bloqueo_id: str) -> Optional[BloqueoHabitacionDB]:
    return db.scalar(select(BloqueoHabitacionDB).where(BloqueoHabitacionDB.bloqueo_id == bloqueo_id))


def expire_block(db: Session, bloqueo: BloqueoHabitacionDB):
    bloqueo.estado = "expirado"
    db.add(bloqueo)
    db.commit()


def confirm_block(db: Session, bloqueo: BloqueoHabitacionDB, reserva_id: str):
    bloqueo.estado = "confirmado"
    bloqueo.reserva_id = reserva_id
    db.add(bloqueo)
    db.commit()
    db.refresh(bloqueo)
    return bloqueo


def delete_block(db: Session, bloqueo: BloqueoHabitacionDB):
    db.delete(bloqueo)
    db.commit()
