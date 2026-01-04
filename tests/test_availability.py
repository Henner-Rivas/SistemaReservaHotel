from datetime import date
from fastapi.testclient import TestClient

from services.auth.main import app as auth_app
from services.availability.main import app as availability_app
from shared.database import Base, engine, SessionLocal
from services.availability.models import HabitacionDB


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # seed a room
        room = HabitacionDB(
            habitacion_id="HAB001",
            hotel_id="HOTEL1",
            numero="101",
            tipo="standard",
            piso=1,
            capacidad_maxima=2,
            precio_base=100.00,
            caracteristicas=["wifi", "tv"],
            activa=True,
        )
        db.add(room)
        db.commit()
    finally:
        db.close()


def test_search_and_block_flow():
    # Obtain token
    aclient = TestClient(auth_app)
    reg = aclient.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "tester",
            "password": "Password1",
            "nombre_completo": "Tester",
        },
    )
    assert reg.status_code in (200, 201)
    login = aclient.post("/api/v1/auth/login", json={"username": "tester", "password": "Password1"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client = TestClient(availability_app)

    # Search availability
    r = client.post(
        "/api/v1/availability/search",
        json={
            "hotel_id": "HOTEL1",
            "fecha_inicio": str(date.today()),
            "fecha_fin": str(date.today().replace(day=date.today().day + 1)),
            "numero_huespedes": 2,
        },
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_disponibles"] >= 1

    # Block the room
    blk = client.post(
        "/api/v1/availability/block",
        json={
            "habitacion_id": "HAB001",
            "fecha_inicio": str(date.today()),
            "fecha_fin": str(date.today().replace(day=date.today().day + 1)),
            "duracion_minutos": 15,
        },
        headers=headers,
    )
    assert blk.status_code == 200
    bloqueo_id = blk.json()["bloqueo_id"]

    # Search again should return zero
    r2 = client.post(
        "/api/v1/availability/search",
        json={
            "hotel_id": "HOTEL1",
            "fecha_inicio": str(date.today()),
            "fecha_fin": str(date.today().replace(day=date.today().day + 1)),
            "numero_huespedes": 2,
        },
        headers=headers,
    )
    assert r2.status_code == 200
    assert r2.json()["total_disponibles"] == 0

    # Release block
    rel = client.delete(f"/api/v1/availability/block/{bloqueo_id}", headers=headers)
    assert rel.status_code == 200

