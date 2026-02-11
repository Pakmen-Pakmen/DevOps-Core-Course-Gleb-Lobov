import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()

    assert "service" in data
    assert "system" in data
    assert "runtime" in data
    assert data["service"]["name"] == "devops-info-service"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert "uptime_seconds" in data


def test_404_handler(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Not Found"
