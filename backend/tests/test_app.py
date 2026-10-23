"""
Testy jednostkowe dla backendu Task Trackera.
===============================================
Używamy wbudowanego klienta testowego Flaska + bazy SQLite w pamięci,
żeby testy były szybkie, powtarzalne i niezależne od prawdziwego PostgreSQL.
"""

import pytest

import app as app_module


@pytest.fixture
def client():
    """
    🔴 MUST KNOW: w testach NIGDY nie łączymy się z prawdziwą bazą (nawet tą
    z docker-compose) — testy muszą być w pełni odizolowane i powtarzalne,
    niezależnie od tego, co akurat siedzi w Postgresie.
    """
    app_module.app.config["TESTING"] = True
    app_module.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app_module.app.app_context():
        app_module.db.create_all()
        with app_module.app.test_client() as test_client:
            yield test_client
        app_module.db.drop_all()


def test_health_endpoint(client):
    """Liveness probe zawsze powinien odpowiadać 200, niezależnie od bazy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_ready_endpoint(client):
    """Readiness probe sprawdza bazę — tu baza (sqlite in-memory) działa, więc 200."""
    response = client.get("/ready")
    assert response.status_code == 200


def test_create_task_requires_title(client):
    """Walidacja: brak 'title' powinien zwrócić 400, nie 500."""
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400


def test_create_and_list_task(client):
    """Pełny cykl: tworzymy zadanie, sprawdzamy że pojawia się na liście."""
    create_resp = client.post("/api/tasks", json={"title": "Naucz sie CI/CD"})
    assert create_resp.status_code == 201
    created = create_resp.get_json()
    assert created["title"] == "Naucz sie CI/CD"
    assert created["is_done"] is False

    list_resp = client.get("/api/tasks")
    assert list_resp.status_code == 200
    tasks = list_resp.get_json()
    assert len(tasks) == 1


def test_toggle_task_done(client):
    """Oznaczenie zadania jako wykonane powinno zmienić is_done na True."""
    created = client.post("/api/tasks", json={"title": "Test toggle"}).get_json()
    task_id = created["id"]

    update_resp = client.put(f"/api/tasks/{task_id}", json={"is_done": True})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["is_done"] is True


def test_delete_task(client):
    """Usuniete zadanie nie powinno juz pojawiac sie na liscie."""
    created = client.post("/api/tasks", json={"title": "Do usuniecia"}).get_json()
    task_id = created["id"]

    delete_resp = client.delete(f"/api/tasks/{task_id}")
    assert delete_resp.status_code == 204

    list_resp = client.get("/api/tasks")
    assert len(list_resp.get_json()) == 0
