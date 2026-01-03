from __future__ import annotations

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.notifications.service import notification_service


app = FastAPI(title="Notifications Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/notifications/history")
def history(cliente_id: str | None = None) -> Dict:
    return {"notificaciones": notification_service.history(cliente_id)}


@app.get("/api/v1/notifications/stats")
def stats() -> Dict[str, int]:
    return notification_service.stats()


@app.post("/api/v1/notifications/publish")
def publish(evento: str | None = None, datos: Dict | None = None) -> Dict[str, str]:
    if not evento or datos is None:
        return {"message": "evento o datos faltantes"}
    # Directly push to service history
    from shared.events import event_bus

    event_bus.publicar(evento, datos)
    return {"message": "publicado"}
