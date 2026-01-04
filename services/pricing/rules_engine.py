from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, List


BASE_PRICES = {
    "standard": Decimal("100.00"),
    "deluxe": Decimal("180.00"),
    "suite": Decimal("300.00"),
}


def season_multiplier(d: date) -> Decimal:
    # alta: dic, ene, jul, ago => +30%; media: nov, feb, jun => +15%
    alta = {12, 1, 7, 8}
    media = {11, 2, 6}
    if d.month in alta:
        return Decimal("1.30")
    if d.month in media:
        return Decimal("1.15")
    return Decimal("1.00")


def nights_between(start: date, end: date) -> int:
    return (end - start).days


def additional_services_cost(nights: int, services: List[str]) -> Decimal:
    total = Decimal("0.00")
    for s in services or []:
        if s == "desayuno":
            total += Decimal("20.00") * nights
        elif s == "parking":
            total += Decimal("10.00") * nights
        elif s == "spa":
            total += Decimal("50.00")
    return total


def long_stay_discount(nights: int, subtotal: Decimal) -> Decimal:
    if nights >= 14:
        return (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    if nights >= 7:
        return (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
    return Decimal("0.00")


def calculate_price(hotel_id: str, tipo_habitacion: str, fecha_inicio: date, fecha_fin: date, servicios_adicionales: List[str] | None, codigo_promocional: str | None) -> Dict:
    nights = nights_between(fecha_inicio, fecha_fin)
    base = BASE_PRICES.get(tipo_habitacion, Decimal("100.00"))
    mult = season_multiplier(fecha_inicio)
    nightly = (base * mult).quantize(Decimal("0.01"))
    room_cost = (nightly * nights).quantize(Decimal("0.01"))
    services_cost = additional_services_cost(nights, servicios_adicionales or [])
    subtotal = (room_cost + services_cost).quantize(Decimal("0.01"))
    desc_long = long_stay_discount(nights, subtotal)
    # coupon simple: 10% if code == PROMO10
    desc_coupon = Decimal("0.00")
    if codigo_promocional == "PROMO10":
        desc_coupon = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    descuentos = (desc_long + desc_coupon).quantize(Decimal("0.01"))
    taxable = (subtotal - descuentos).quantize(Decimal("0.01"))
    impuestos = (taxable * Decimal("0.18")).quantize(Decimal("0.01"))
    total = (taxable + impuestos).quantize(Decimal("0.01"))
    desglose = [
        {"concepto": "precio_base", "monto": str(room_cost)},
        {"concepto": "servicios", "monto": str(services_cost)},
        {"concepto": "descuento_estancia", "monto": str(desc_long)},
        {"concepto": "descuento_cupon", "monto": str(desc_coupon)},
        {"concepto": "impuestos", "monto": str(impuestos)},
    ]
    return {
        "subtotal": str(subtotal),
        "impuestos": str(impuestos),
        "servicios_adicionales": str(services_cost),
        "descuentos": str(descuentos),
        "total": str(total),
        "moneda": "USD",
        "desglose": desglose,
        "noches": nights,
        "precio_noche": str(nightly),
    }
