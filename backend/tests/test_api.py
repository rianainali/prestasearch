import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    from main import app, vector_store, embed_svc
    from models import Prestataire
    import numpy as np

    # Skip lifespan seed loading — add one prestataire manually for tests
    prestataire = Prestataire(
        name="Test Plumber",
        specialty="Plumbing",
        description="Plumber for tests",
        services=["repair", "troubleshooting"],
        city="Paris",
        country="France",
        hourly_rate=50.0,
    )
    fake_embedding = np.random.randn(3072).astype(np.float32)
    fake_embedding /= np.linalg.norm(fake_embedding)
    vector_store.add(prestataire, fake_embedding)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup
    vector_store.prestataires.clear()
    vector_store.vectors = None


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["prestataire_count"] >= 1


@pytest.mark.anyio
async def test_list_prestataires(client):
    resp = await client.get("/prestataires")
    assert resp.status_code == 200
    prestataires = resp.json()
    assert len(prestataires) >= 1
    assert prestataires[0]["name"] == "Test Plumber"


@pytest.mark.anyio
async def test_search(client):
    resp = await client.post("/search", json={"text": "plumber leak"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert "prestataire" in results[0]
    assert "similarity_score" in results[0]


@pytest.mark.anyio
async def test_search_empty_query(client):
    resp = await client.post("/search", json={})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_add_prestataire(client):
    resp = await client.post(
        "/prestataires",
        data={
            "name": "New Electrician",
            "specialty": "Electrical",
            "description": "Certified electrician",
            "services": "installation, troubleshooting",
            "city": "Lyon",
            "hourly_rate": "45",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "prestataire_id" in data
