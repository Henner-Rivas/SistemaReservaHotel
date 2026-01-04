from __future__ import annotations

from datetime import datetime
import asyncio
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import Base, engine, get_db
from shared.security import verify_token
from services.availability.models import HabitacionDB, BloqueoHabitacionDB
from services.availability.schemas import (
    BloquearHabitacionRequest,
    BloqueoResponse,
    ConsultaDisponibilidadRequest,
    DisponibilidadResponse,
    HabitacionDisponible,
)
from services.availability.service import (
    block_room,
    cleanup_expired_blocks,
    confirm_block_reservation,
    search_availability,
    release_block,
)


app = FastAPI(title="Availability Service", version="1.0.0")

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


@app.post("/api/v1/availability/search")
def search(payload: ConsultaDisponibilidadRequest, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> DisponibilidadResponse:
    habitaciones = [
        HabitacionDisponible(**h) for h in search_availability(
            db,
            payload.hotel_id,
            payload.fecha_inicio,
            payload.fecha_fin,
            payload.tipo_habitacion,
            payload.precio_maximo,
        )
    ]
    return DisponibilidadResponse(
        hotel_id=payload.hotel_id,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        noches=(payload.fecha_fin - payload.fecha_inicio).days,
        habitaciones=habitaciones,
        total_disponibles=len(habitaciones),
    )


@app.post("/api/v1/availability/block")
def block(payload: BloquearHabitacionRequest, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> BloqueoResponse:
    data = block_room(db, payload.habitacion_id, payload.fecha_inicio, payload.fecha_fin, payload.duracion_minutos)
    return BloqueoResponse(**data)


@app.delete("/api/v1/availability/block/{bloqueo_id}")
def release(bloqueo_id: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> Dict[str, str]:
    release_block(db, bloqueo_id)
    return {"message": "bloqueo liberado"}


@app.post("/api/v1/availability/confirm")
def confirm(payload: Dict[str, str], current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> Dict:
    result = confirm_block_reservation(db, payload["bloqueo_id"], payload.get("reserva_id", ""))
    return result


@app.get("/api/v1/availability/rooms")
def rooms(hotel_id: str, tipo: str | None = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)) -> Dict:
    from services.availability.repository import list_rooms_by_hotel

    rooms = list_rooms_by_hotel(db, hotel_id, tipo)
    return {"habitaciones": [
        {
            "habitacion_id": r.habitacion_id,
            "numero": r.numero,
            "tipo": r.tipo,
            "piso": r.piso,
            "capacidad_maxima": r.capacidad_maxima,
            "precio_base": str(r.precio_base),
            "caracteristicas": r.caracteristicas or [],
        }
        for r in rooms
    ]}


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    # Background task: cleanup expired blocks every 5 minutes
    async def cleaner():
        while True:
            # Use a new DB session for each cleanup
            from shared.database import SessionLocal

            db = SessionLocal()
            try:
                cleanup_expired_blocks(db)
            finally:
                db.close()
            await asyncio.sleep(300)

    asyncio.create_task(cleaner())

    # Seed example rooms if empty (insert 10 demo rooms)
    from shared.database import SessionLocal
    from sqlalchemy import select
    db = SessionLocal()
    try:
        from services.availability.models import HabitacionDB
        existing = list(db.scalars(select(HabitacionDB)))
        if len(existing) == 0:
            demo_rooms = []
            # Generate HAB001..HAB010 with a mix of types
            for i in range(1, 11):
                hab_id = f"HAB{str(i).zfill(3)}"
                numero = str(100 + i)
                # Cycle types: standard, deluxe, suite
                tipos = ["standard", "deluxe", "suite"]
                tipo = tipos[(i - 1) % len(tipos)]
                piso = 1 + ((i - 1) // 4)
                capacidad = 2 if tipo == "standard" else (3 if tipo == "deluxe" else 4)
                precio = 100.00 if tipo == "standard" else (180.00 if tipo == "deluxe" else 250.00)
                caracteristicas = ["wifi", "tv"] + (["mini-bar"] if tipo != "standard" else [])
                demo_rooms.append(
                    HabitacionDB(
                        habitacion_id=hab_id,
                        hotel_id="HOTEL1",
                        numero=numero,
                        tipo=tipo,
                        piso=piso,
                        capacidad_maxima=capacidad,
                        precio_base=precio,
                        caracteristicas=caracteristicas,
                        activa=True,
                    )
                )
            for r in demo_rooms:
                db.add(r)
            db.commit()
    finally:
        db.close()
