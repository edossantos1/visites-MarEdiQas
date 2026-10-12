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


def test_root_version_header(client):
    resp = client.get("/")
    assert resp.headers["X-Visites-Version"] == "0.1.0"


def test_version_header_et_compteur(client):
    r1 = client.get("/")
    r2 = client.get("/")
    assert r2.headers["X-Visites-Version"] == "0.1.0"
    assert r2.json()["visites"] == r1.json()["visites"] + 1


def test_reset(client):
    client.get("/")
    resp = client.post("/reset")
    assert resp.status_code == 200
    assert resp.json() == {"visites": 0}
    assert client.get("/").json() == {"visites": 1}
