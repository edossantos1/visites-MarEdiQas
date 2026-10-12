import fakeredis
import pytest
from fastapi.testclient import TestClient

import app.main as main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "r", fakeredis.FakeRedis(decode_responses=True))
    return TestClient(main.app)


def test_root_incremente(client):
    assert client.get("/").json() == {"visites": 1}
    assert client.get("/").json() == {"visites": 2}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics(client):
    client.get("/")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text
