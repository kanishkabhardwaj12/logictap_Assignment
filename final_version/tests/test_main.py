import pytest
import sqlite3
from fastapi.testclient import TestClient

from app.database import CallDatabase
from app.main import create_app


@pytest.fixture
def client(tmp_path) -> TestClient:
    test_database = CallDatabase(tmp_path / "calls.db")
    return TestClient(create_app(test_database))


def test_call_is_stored_and_can_be_retrieved(client: TestClient) -> None:
    payload = {"call_id": "abc123", "status": "answered", "duration_secs": 42}

    response = client.post("/call-ended", json=payload)

    assert response.status_code == 200
    assert response.json() == payload
    assert client.get("/calls/abc123").json() == payload


def test_duplicate_call_id_does_not_create_a_second_record(
    client: TestClient,
) -> None:
    first = {"call_id": "abc123", "status": "answered", "duration_secs": 42}
    duplicate = {"call_id": "abc123", "status": "missed", "duration_secs": 0}

    assert client.post("/call-ended", json=first).status_code == 200
    response = client.post("/call-ended", json=duplicate)

    assert response.status_code == 200
    assert response.json() == first


def test_missing_call_id_is_rejected_with_a_clear_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
        "/call-ended",
        json={"status": "answered", "duration_secs": 42},
    )

    assert response.status_code == 422
    assert "call_id" in response.text


def test_unknown_call_returns_not_found(client: TestClient) -> None:
    response = client.get("/calls/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Call 'does-not-exist' was not found"
    }


def test_records_persist_in_sqlite(tmp_path) -> None:
    database_path = tmp_path / "calls.db"
    first_database = CallDatabase(database_path)
    payload = {"call_id": "persistent-1", "status": "answered", "duration_secs": 7}

    first_database.save_if_new(**payload)

    restarted_database = CallDatabase(database_path)

    assert restarted_database.get("persistent-1") == payload
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM calls").fetchone()[0] == 1
