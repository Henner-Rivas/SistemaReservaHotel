from shared.events import event_bus
from services.notifications.service import notification_service


def test_notifications_capture_events():
    # Ensure clean history for this test context
    # Note: EventBus keeps global history; we focus on notification_service history
    # Publish a few events
    event_bus.publicar("reserva.creada", {"reserva_id": "R1", "cliente_id": "C1"})
    event_bus.publicar("pago.aprobado", {"transaccion_id": "TX1", "reserva_id": "R1", "cliente_id": "C1", "monto": "100.00"})
    event_bus.publicar("reserva.cancelada", {"reserva_id": "R2", "cliente_id": "C2"})

    hist = notification_service.history()
    assert any(h["evento"] == "reserva.creada" and h["datos"]["reserva_id"] == "R1" for h in hist)
    assert any(h["evento"] == "pago.aprobado" and h["datos"]["transaccion_id"] == "TX1" for h in hist)
    assert any(h["evento"] == "reserva.cancelada" and h["datos"]["reserva_id"] == "R2" for h in hist)

    # Stats should count by event type
    stats = notification_service.stats()
    assert stats.get("reserva.creada", 0) >= 1
    assert stats.get("pago.aprobado", 0) >= 1
    assert stats.get("reserva.cancelada", 0) >= 1
