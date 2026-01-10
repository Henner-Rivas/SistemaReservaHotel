import os
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

os.environ["USE_SQLITE_FOR_TESTS"] = "1"
from shared.database import Base, engine
from shared.security import create_access_token
from shared.events import event_bus
from services.notifications.service import notification_service
from services.reservations.main import app as reservations_app
from shared.http_client import ServiceClient


def setup_module(module):
    # Ensure DB tables exist for reservations and payments
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clear_event_history():
    # EventBus keeps global history; no API to clear, but notification_service keeps own history
    # We cannot fully clear EventBus history; focus on notification_service which we can observe
    notification_service._history.clear()
    yield


def _stub_methods(monkeypatch):
    async def _get_customer(self, cliente_id: str, token: str):
        return {"cliente_id": cliente_id, "nombre": "Cliente Test"}

    async def _calculate_price(self, params, token: str):
        return {"total": "120.00", "detalles": {"base": "100.00", "impuestos": "20.00"}}

    async def _check_availability(self, params, token: str):
        return {"total_disponibles": 1, "habitaciones": [{"habitacion_id": "HAB001"}]}

    async def _availability_block(self, params, token: str):
        return {"bloqueo_id": "BLK001", "estado": "bloqueada"}

    async def _process_payment(self, params, token: str):
        return {"transaccion_id": "TX001", "estado": "aprobado", "monto": params["monto"]}

    async def _availability_confirm(self, params, token: str):
        return {"estado": "confirmada"}

    async def _publish_notification(self, event: str, data: dict):
        # Simulate successful publish without external HTTP
        event_bus.publicar(event, data)
        return {"message": "publicado"}

    monkeypatch.setattr(ServiceClient, "get_customer", _get_customer, raising=True)
    monkeypatch.setattr(ServiceClient, "calculate_price", _calculate_price, raising=True)
    monkeypatch.setattr(ServiceClient, "check_availability", _check_availability, raising=True)
    monkeypatch.setattr(ServiceClient, "availability_block", _availability_block, raising=True)
    monkeypatch.setattr(ServiceClient, "process_payment", _process_payment, raising=True)
    monkeypatch.setattr(ServiceClient, "availability_confirm", _availability_confirm, raising=True)
    monkeypatch.setattr(ServiceClient, "publish_notification", _publish_notification, raising=True)


def test_create_reservation_end_to_end(monkeypatch):
    _stub_methods(monkeypatch)
    client = TestClient(reservations_app)

    token = create_access_token({"usuario_id": "U1", "username": "tester", "rol": "cliente"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "cliente_id": "C1",
        "hotel_id": "HOTEL1",
        "tipo_habitacion": "standard",
        "fecha_inicio": str(date.today()),
        "fecha_fin": str(date.today().replace(day=date.today().day + 1)),
        "metodo_pago": {"tipo": "tarjeta", "token": "tok_test"},
    }

    r = client.post("/api/v1/reservations", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["estado"] == "CONFIRMADA"
    assert "reserva_id" in data["detalles"]

    # Notifications service should have captured reserva.creada event
    hist = notification_service.history("C1")
    assert any(h["evento"] == "reserva.creada" for h in hist)
