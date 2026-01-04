from __future__ import annotations

from sqlalchemy.orm import Session

from services.customers.models import ClienteDB
from services.customers.repository import create_customer, get_customer, update_customer
from shared.exceptions import NotFoundError


def create_customer_service(db: Session, data: dict) -> ClienteDB:
    return create_customer(db, data)


def get_customer_service(db: Session, cliente_id: str) -> ClienteDB:
    cliente = get_customer(db, cliente_id)
    if not cliente:
        raise NotFoundError("Cliente no encontrado")
    return cliente


def update_customer_service(db: Session, cliente_id: str, data: dict) -> ClienteDB:
    cliente = get_customer_service(db, cliente_id)
    return update_customer(db, cliente, data)
