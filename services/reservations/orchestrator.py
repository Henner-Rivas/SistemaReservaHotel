from __future__ import annotations

from typing import Dict

from shared.http_client import ServiceClient


class CrearReservaOrchestrator:
    """
    Orquesta el proceso completo de crear una reserva:
    1. Validar datos
    2. Obtener info cliente (Customer Service)
    3. Consultar disponibilidad (Availability Service)
    4. Calcular precio (Pricing Service)
    5. Bloquear habitación (Availability Service)
    6. Procesar pago (Payment Service)
    7. Crear reserva en BD
    8. Confirmar bloqueo (Availability Service)
    9. Publicar evento "reserva.creada"
    Si algo falla, implementar compensaciones (Saga pattern).
    """

    def __init__(self):
        self.client = ServiceClient()

    async def crear_reserva(self, payload: Dict, token: str) -> Dict:
        # 1. Obtener cliente
        cliente = await self.client.get_customer(payload["cliente_id"], token)
        # 2. Calcular precio
        precio = await self.client.calculate_price(
            {
                "hotel_id": payload["hotel_id"],
                "tipo_habitacion": payload["tipo_habitacion"],
                "fecha_inicio": payload["fecha_inicio"],
                "fecha_fin": payload["fecha_fin"],
                "servicios_adicionales": payload.get("servicios_adicionales", []),
                "codigo_promocional": payload.get("codigo_promocional"),
            },
            token,
        )
        # 3. Buscar disponibilidad y elegir una habitación si no viene especificada
        habitacion_id = payload.get("habitacion_id")
        if not habitacion_id:
            dispo = await self.client.check_availability(
                {
                    "hotel_id": payload["hotel_id"],
                    "fecha_inicio": payload["fecha_inicio"],
                    "fecha_fin": payload["fecha_fin"],
                    "tipo_habitacion": payload.get("tipo_habitacion"),
                    "numero_huespedes": payload.get("numero_huespedes", 2),
                    "precio_maximo": None,
                },
                token,
            )
            habitaciones = dispo.get("habitaciones", [])
            if not habitaciones:
                raise ValueError("No hay habitaciones disponibles para el rango solicitado")
            habitacion_id = habitaciones[0]["habitacion_id"]

        # 4. Bloquear habitación (temporal)
        block = await self.client.availability_block(
            {
                "habitacion_id": habitacion_id,
                "fecha_inicio": payload["fecha_inicio"],
                "fecha_fin": payload["fecha_fin"],
                "duracion_minutos": 15,
            },
            token,
        )
        # 5. Procesar pago
        pago = await self.client.process_payment(
            {
                "cliente_id": payload["cliente_id"],
                "reserva_id": None,
                "monto": precio["total"],
                "moneda": "USD",
                "metodo_pago": payload["metodo_pago"],
            },
            token,
        )
        return {"cliente": cliente, "precio": precio, "pago": pago, "bloqueo": block, "estado": "CREADA", "habitacion_id": habitacion_id}
