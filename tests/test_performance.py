import time
from datetime import date

import pytest
from fastapi.testclient import TestClient

from shared.security import create_access_token
from services.reservations.main import app as reservations_app
from shared.http_client import ServiceClient
from shared.events import event_bus


def _stub_methods(monkeypatch):
    async def _get_customer(self, cliente_id: str, token: str):
        return {"cliente_id": cliente_id}

    async def _calculate_price(self, params, token: str):
        return {"total": "100.00"}

    async def _check_availability(self, params, token: str):
        return {"total_disponibles": 1, "habitaciones": [{"habitacion_id": "HAB001"}]}

    async def _availability_block(self, params, token: str):
        return {"bloqueo_id": "BLK001"}

    async def _process_payment(self, params, token: str):
        return {"transaccion_id": "TX001", "estado": "aprobado", "monto": params["monto"]}

    async def _availability_confirm(self, params, token: str):
        return {"estado": "confirmada"}

    async def _publish_notification(self, event: str, data: dict):
        event_bus.publicar(event, data)
        return {"message": "publicado"}

    monkeypatch.setattr(ServiceClient, "get_customer", _get_customer, raising=True)
    monkeypatch.setattr(ServiceClient, "calculate_price", _calculate_price, raising=True)
    monkeypatch.setattr(ServiceClient, "check_availability", _check_availability, raising=True)
    monkeypatch.setattr(ServiceClient, "availability_block", _availability_block, raising=True)
    monkeypatch.setattr(ServiceClient, "process_payment", _process_payment, raising=True)
    monkeypatch.setattr(ServiceClient, "availability_confirm", _availability_confirm, raising=True)
    monkeypatch.setattr(ServiceClient, "publish_notification", _publish_notification, raising=True)


@pytest.mark.performance
def test_reservation_creation_throughput(monkeypatch):
    _stub_methods(monkeypatch)
    client = TestClient(reservations_app)
    token = create_access_token({"usuario_id": "U1", "username": "perf", "rol": "cliente"})
    headers = {"Authorization": f"Bearer {token}"}

    payload_template = {
        "cliente_id": "C_PERF",
        "hotel_id": "HOTEL1",
        "tipo_habitacion": "standard",
        "fecha_inicio": str(date.today()),
        "fecha_fin": str(date.today().replace(day=date.today().day + 1)),
        "metodo_pago": {"tipo": "tarjeta", "token": "tok_perf"},
    }

    start = time.perf_counter()
    N = 10
    for i in range(N):
        r = client.post("/api/v1/reservations", json=payload_template, headers=headers)
        assert r.status_code == 200
    duration = time.perf_counter() - start
    avg = duration / N
    # Expect average under 0.2s with stubs
    assert avg < 0.2
