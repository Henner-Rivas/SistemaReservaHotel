from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import Base, engine, get_db
from shared.events import event_bus
from shared.security import verify_token
from services.payments.models import TransaccionDB
from services.payments.schemas import ProcesarPagoRequest, ReembolsarRequest, TransaccionResponse
from services.payments.simulator import simular_procesamiento_pago


app = FastAPI(title="Payments Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/payments/process")
def process_payment(payload: ProcesarPagoRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> TransaccionResponse:
    sim = simular_procesamiento_pago(payload.monto, payload.metodo_pago.token)
    tx = TransaccionDB(
        transaccion_id=f"TX_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        cliente_id=payload.cliente_id,
        reserva_id=payload.reserva_id,
        monto=Decimal(payload.monto),
        moneda=payload.moneda,
        tipo="cargo",
        metodo_pago=payload.metodo_pago.tipo,
        estado="aprobado" if sim.get("aprobado") else "rechazado",
        codigo_aprobacion=sim.get("codigo"),
        codigo_error=None if sim.get("aprobado") else sim.get("codigo"),
        mensaje_error=None if sim.get("aprobado") else sim.get("mensaje"),
        procesado_en=datetime.utcnow(),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # Publish events
    if sim.get("aprobado"):
        event_bus.publicar("pago.aprobado", {"transaccion_id": tx.transaccion_id, "reserva_id": payload.reserva_id, "cliente_id": payload.cliente_id, "monto": str(payload.monto)})
    else:
        event_bus.publicar("pago.rechazado", {"transaccion_id": tx.transaccion_id, "reserva_id": payload.reserva_id, "cliente_id": payload.cliente_id, "monto": str(payload.monto), "error": sim.get("mensaje")})

    return TransaccionResponse(
        transaccion_id=tx.transaccion_id,
        estado=tx.estado,
        monto=Decimal(tx.monto),
        codigo_aprobacion=tx.codigo_aprobacion,
        mensaje=sim.get("mensaje", "OK"),
        procesado_en=tx.procesado_en,
    )


@app.post("/api/v1/payments/refund")
def refund(payload: ReembolsarRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> Dict[str, str]:
    # Simplificado: registrar reembolso
    tx = TransaccionDB(
        transaccion_id=f"RF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        cliente_id="",
        reserva_id=None,
        monto=Decimal(payload.monto),
        moneda="USD",
        tipo="reembolso",
        metodo_pago="",
        estado="reembolsado",
        procesado_en=datetime.utcnow(),
    )
    db.add(tx)
    db.commit()
    return {"message": "reembolso procesado", "transaccion_id": tx.transaccion_id}


@app.get("/api/v1/payments/by-reservation/{reserva_id}")
def payments_by_reservation(reserva_id: str, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> Dict:
    from sqlalchemy import select
    qs = db.scalars(select(TransaccionDB).where(TransaccionDB.reserva_id == reserva_id))
    return {"transacciones": [
        {
            "transaccion_id": t.transaccion_id,
            "estado": t.estado,
            "monto": str(t.monto),
            "tipo": t.tipo,
            "procesado_en": t.procesado_en,
        }
        for t in qs
    ]}
