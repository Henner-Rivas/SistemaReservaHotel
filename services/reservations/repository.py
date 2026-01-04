from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.reservations.models import ReservaDB


def create_reservation(db: Session, data: dict) -> ReservaDB:
    reserva = ReservaDB(
        reserva_id=str(uuid.uuid4())[:8],
        **data,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def get_reservation(db: Session, reserva_id: str) -> Optional[ReservaDB]:
    return db.scalar(select(ReservaDB).where(ReservaDB.reserva_id == reserva_id))


def list_reservations_by_customer(db: Session, cliente_id: str) -> List[ReservaDB]:
    return list(db.scalars(select(ReservaDB).where(ReservaDB.cliente_id == cliente_id)))


def update_reservation_status(db: Session, reserva: ReservaDB, estado: str) -> ReservaDB:
    reserva.estado = estado
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def update_reservation_fields(db: Session, reserva: ReservaDB, data: dict) -> ReservaDB:
    for k, v in data.items():
        setattr(reserva, k, v)
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva
