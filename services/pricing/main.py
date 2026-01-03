from __future__ import annotations

from decimal import Decimal
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.security import verify_token
from services.pricing.rules_engine import calculate_price
from services.pricing.schemas import CalcularPrecioRequest, DetallesPrecio, ValidarCuponRequest, ValidarCuponResponse


app = FastAPI(title="Pricing Service", version="1.0.0")

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


@app.post("/api/v1/pricing/calculate")
def calculate(payload: CalcularPrecioRequest, current_user: dict = Depends(verify_token)) -> Dict:
    data = calculate_price(
        payload.hotel_id,
        payload.tipo_habitacion,
        payload.fecha_inicio,
        payload.fecha_fin,
        payload.servicios_adicionales or [],
        payload.codigo_promocional,
    )
    return data


@app.post("/api/v1/pricing/validate-coupon")
def validate_coupon(payload: ValidarCuponRequest, current_user: dict = Depends(verify_token)) -> ValidarCuponResponse:
    if payload.codigo == "PROMO10":
        descuento = (payload.monto * Decimal("0.10")).quantize(Decimal("0.01"))
        return ValidarCuponResponse(codigo=payload.codigo, valido=True, descuento=descuento, mensaje="Cupón válido")
    return ValidarCuponResponse(codigo=payload.codigo, valido=False, descuento=Decimal("0.00"), mensaje="Cupón inválido")


@app.get("/api/v1/pricing/promotions")
def promotions(current_user: dict = Depends(verify_token)) -> Dict:
    return {"promociones": [{"codigo": "PROMO10", "descripcion": "10% de descuento"}]}
