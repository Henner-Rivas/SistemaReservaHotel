from __future__ import annotations

from typing import Any, Dict
from datetime import date, datetime
from decimal import Decimal

import httpx
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    CUSTOMERS_SERVICE_URL: str = "http://localhost:8001"
    AVAILABILITY_SERVICE_URL: str = "http://localhost:8002"
    PRICING_SERVICE_URL: str = "http://localhost:8003"
    PAYMENTS_SERVICE_URL: str = "http://localhost:8004"
    RESERVATIONS_SERVICE_URL: str = "http://localhost:8005"
    NOTIFICATIONS_SERVICE_URL: str = "http://localhost:8006"

    class Config:
        env_file = ".env"


settings = Settings()


class ServiceClient:
    """Cliente HTTP para comunicarse con otros servicios"""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=10.0)

    async def get_customer(self, cliente_id: str, token: str) -> Dict[str, Any]:
        url = f"{settings.CUSTOMERS_SERVICE_URL}/api/v1/customers/{cliente_id}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def check_availability(self, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        url = f"{settings.AVAILABILITY_SERVICE_URL}/api/v1/availability/search"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json=_to_jsonable(params), headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def calculate_price(self, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        url = f"{settings.PRICING_SERVICE_URL}/api/v1/pricing/calculate"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json=_to_jsonable(params), headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def process_payment(self, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        url = f"{settings.PAYMENTS_SERVICE_URL}/api/v1/payments/process"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json=_to_jsonable(params), headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def availability_block(self, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        url = f"{settings.AVAILABILITY_SERVICE_URL}/api/v1/availability/block"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json=_to_jsonable(params), headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def availability_confirm(self, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        url = f"{settings.AVAILABILITY_SERVICE_URL}/api/v1/availability/confirm"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json=_to_jsonable(params), headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def publish_notification(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{settings.NOTIFICATIONS_SERVICE_URL}/api/v1/notifications/publish"
        resp = await self._client.post(url, json={"evento": event, "datos": data})
        resp.raise_for_status()
        return resp.json()

    async def payments_by_reservation(self, reserva_id: str, token: str) -> Dict[str, Any]:
        url = f"{settings.PAYMENTS_SERVICE_URL}/api/v1/payments/by-reservation/{reserva_id}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def refund_payment(self, transaccion_id: str, monto: str, token: str) -> Dict[str, Any]:
        url = f"{settings.PAYMENTS_SERVICE_URL}/api/v1/payments/refund"
        headers = {"Authorization": f"Bearer {token}"}
        resp = await self._client.post(url, json={"transaccion_id": transaccion_id, "monto": monto}, headers=headers)
        resp.raise_for_status()
        return resp.json()


def _to_jsonable(value: Any) -> Any:
    """Recursively convert dates/datetimes/decimals to JSON-serializable forms."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value
