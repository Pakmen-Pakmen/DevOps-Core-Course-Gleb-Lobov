import pytest
from app import app


@pytest.fixture
def visits_file(tmp_path, monkeypatch):
    visits_file = tmp_path / "visits"
    monkeypatch.setenv("VISITS_FILE", str(visits_file))
    return visits_file


@pytest.fixture
def client(visits_file):
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
    assert "stats" in data
    assert data["stats"]["visits"] == 1
    assert data["service"]["name"] == "devops-info-service"
    assert data["service"]["version"] == "1.0.1"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert "uptime_seconds" in data


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"


def test_visits_endpoint(client):
    client.get("/")
    client.get("/")
    response = client.get("/visits")
    assert response.status_code == 200
    data = response.get_json()
    assert data["visits"] == 2


def test_visits_file_persists_counter(client, visits_file):
    client.get("/")
    response = client.get("/visits")
    assert response.status_code == 200
    data = response.get_json()
    assert data["visits"] == 1
    assert visits_file.exists()
    assert visits_file.read_text(encoding="utf-8").strip() == "1"


def test_404_handler(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Not Found"
