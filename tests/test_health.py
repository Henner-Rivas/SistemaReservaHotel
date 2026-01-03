from fastapi.testclient import TestClient

from services.auth.main import app as auth_app
from services.customers.main import app as customers_app
from services.availability.main import app as availability_app
from services.pricing.main import app as pricing_app
from services.payments.main import app as payments_app
from services.reservations.main import app as reservations_app
from services.notifications.main import app as notifications_app


def test_health_auth():
    client = TestClient(auth_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_customers():
    client = TestClient(customers_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_availability():
    client = TestClient(availability_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_pricing():
    client = TestClient(pricing_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_payments():
    client = TestClient(payments_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_reservations():
    client = TestClient(reservations_app)
    r = client.get('/health')
    assert r.status_code == 200


def test_health_notifications():
    client = TestClient(notifications_app)
    r = client.get('/health')
    assert r.status_code == 200
