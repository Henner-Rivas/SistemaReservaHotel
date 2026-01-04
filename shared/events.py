from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """Event Bus con soporte para eventos asíncronos y logging mejorado"""

    _instance: "EventBus" | None = None
    _suscriptores: Dict[str, List[Callable]]
    _event_history: List[dict]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._suscriptores = {}
            cls._instance._event_history = []
        return cls._instance

    def suscribir(self, tipo_evento: str, callback: Callable):
        self._suscriptores.setdefault(tipo_evento, []).append(callback)

    def publicar(self, tipo_evento: str, datos: dict):
        """Publica un evento a todos los suscriptores"""
        evento = {
            "tipo": tipo_evento,
            "datos": datos,
            "timestamp": datetime.now().isoformat(),
            "evento_id": str(uuid.uuid4()),
        }

        self._event_history.append(evento)
        logger.info(f"Evento publicado: {tipo_evento} -> {datos}")

        if tipo_evento in self._suscriptores:
            for callback in list(self._suscriptores[tipo_evento]):
                try:
                    callback(datos)
                except Exception as e:
                    logger.error(f"Error en callback para {tipo_evento}: {e}")

    def obtener_historial(self, filtro_tipo: str | None = None) -> List[dict]:
        if filtro_tipo:
            return [e for e in self._event_history if e["tipo"] == filtro_tipo]
        return list(self._event_history)


event_bus = EventBus()
