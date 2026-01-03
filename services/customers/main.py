from __future__ import annotations

from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import Base, engine, get_db
from shared.security import verify_token
from services.customers.schemas import CrearClienteRequest, ClienteResponse
from services.customers.service import create_customer_service, get_customer_service, update_customer_service


app = FastAPI(title="Customers Service", version="1.0.0")

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


@app.post("/api/v1/customers", status_code=201)
def create_customer(payload: CrearClienteRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> ClienteResponse:
    cliente = create_customer_service(db, payload.model_dump())
    return ClienteResponse(
        cliente_id=cliente.cliente_id,
        nombre_completo=cliente.nombre_completo,
        email=cliente.email,
        telefono=cliente.telefono,
        ciudad=cliente.ciudad,
        pais=cliente.pais,
        creado_en=cliente.creado_en,
    )


@app.get("/api/v1/customers/{cliente_id}")
def get_customer(cliente_id: str, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> ClienteResponse:
    c = get_customer_service(db, cliente_id)
    return ClienteResponse(
        cliente_id=c.cliente_id,
        nombre_completo=c.nombre_completo,
        email=c.email,
        telefono=c.telefono,
        ciudad=c.ciudad,
        pais=c.pais,
        creado_en=c.creado_en,
    )


@app.put("/api/v1/customers/{cliente_id}")
def update_customer(cliente_id: str, payload: CrearClienteRequest, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)) -> Dict[str, str]:
    update_customer_service(db, cliente_id, payload.model_dump())
    return {"message": "cliente actualizado"}
