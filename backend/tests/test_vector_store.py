import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from models import Prestataire
from vector_store import InMemoryVectorStore


@pytest.fixture
def store():
    return InMemoryVectorStore()


def _random_embedding(dim=1408):
    vec = np.random.randn(dim).astype(np.float32)
    return vec / np.linalg.norm(vec)


def _make_prestataire(name: str) -> Prestataire:
    return Prestataire(
        name=name,
        specialty="Test",
        description=f"Description for {name}",
    )


def test_add_and_search(store):
    """Adding a prestataire then searching with its own embedding returns score > 0.99."""
    prestataire = _make_prestataire("Test Plombier")
    embedding = _random_embedding()
    store.add(prestataire, embedding)

    results = store.search(embedding, top_k=5)
    assert len(results) == 1
    assert results[0].prestataire.name == "Test Plombier"
    assert results[0].similarity_score > 0.99


def test_search_empty_store(store):
    """Searching an empty store returns an empty list."""
    query = _random_embedding()
    results = store.search(query, top_k=5)
    assert results == []


def test_top_k_greater_than_n(store):
    """When top_k > number of prestataires, all prestataires are returned."""
    for i in range(3):
        store.add(_make_prestataire(f"Prestataire {i}"), _random_embedding())

    query = _random_embedding()
    results = store.search(query, top_k=10)
    assert len(results) == 3
