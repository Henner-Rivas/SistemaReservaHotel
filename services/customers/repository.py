from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.customers.models import ClienteDB


def create_customer(db: Session, data: dict) -> ClienteDB:
    cliente = ClienteDB(
        cliente_id=str(uuid.uuid4())[:8],
        **data,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def get_customer(db: Session, cliente_id: str) -> Optional[ClienteDB]:
    return db.scalar(select(ClienteDB).where(ClienteDB.cliente_id == cliente_id))


def update_customer(db: Session, cliente: ClienteDB, data: dict) -> ClienteDB:
    for k, v in data.items():
        setattr(cliente, k, v)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente
