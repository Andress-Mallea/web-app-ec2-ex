import pytest

from app import create_app
from app.models import db


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SEED": False})
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def room(client):
    return client.post("/api/rooms", json={"number": "101", "type": "double", "price_per_night": 300, "capacity": 2}).get_json()


@pytest.fixture
def guest(client):
    return client.post("/api/guests", json={"full_name": "Ana Rojas", "email": "ana@example.com", "document": "123"}).get_json()
