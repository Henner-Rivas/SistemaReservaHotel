from __future__ import annotations

from typing import Dict, List

from shared.events import event_bus


class NotificationService:
    def __init__(self):
        self._history: List[Dict] = []
        event_bus.suscribir("reserva.creada", self._on_reserva_creada)
        event_bus.suscribir("reserva.cancelada", self._on_reserva_cancelada)
        event_bus.suscribir("pago.aprobado", self._on_pago_aprobado)
        event_bus.suscribir("pago.rechazado", self._on_pago_rechazado)

    def _save(self, evento: str, datos: Dict):
        self._history.append({"evento": evento, "datos": datos})

    def _on_reserva_creada(self, datos: Dict):
        self._save("reserva.creada", datos)

    def _on_reserva_cancelada(self, datos: Dict):
        self._save("reserva.cancelada", datos)

    def _on_pago_aprobado(self, datos: Dict):
        self._save("pago.aprobado", datos)

    def _on_pago_rechazado(self, datos: Dict):
        self._save("pago.rechazado", datos)

    def history(self, cliente_id: str | None = None) -> List[Dict]:
        if cliente_id:
            return [h for h in self._history if h["datos"].get("cliente_id") == cliente_id]
        return list(self._history)

    def stats(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for h in self._history:
            counts[h["evento"]] = counts.get(h["evento"], 0) + 1
        return counts


notification_service = NotificationService()
