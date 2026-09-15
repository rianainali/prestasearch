import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from models import Prestataire
from embedding_service import EmbeddingService


@pytest.fixture
def embed_svc():
    return EmbeddingService()


@pytest.fixture
def sample_prestataire():
    return Prestataire(
        name="Jean Dupont Plomberie",
        specialty="Plomberie",
        description="Plombier expérimenté spécialisé dans les réparations d'urgence",
        services=["réparation fuite", "débouchage", "installation sanitaire"],
        city="Paris",
        country="France",
        hourly_rate=55.0,
    )


def test_embed_prestataire_happy_path(embed_svc, sample_prestataire):
    """Full prestataire embedding returns a normalized 3072-dim vector."""
    vec = embed_svc.embed_prestataire(sample_prestataire)
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_text_only(embed_svc):
    """Text-only query returns a valid embedding."""
    vec = embed_svc.embed_query(text="plombier urgence fuite")
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_image_only(embed_svc):
    """Image-only query returns a valid embedding."""
    # 1x1 white JPEG
    import base64
    tiny_jpeg = base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS"
        "Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJ"
        "CQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
        "MjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEA"
        "AAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIh"
        "MUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6"
        "Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
        "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx"
        "8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA"
        "AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAV"
        "YnLRChYkNOEl8RcYI4Q/RFhHRUYnJCk2NTc4OTpDREVGR0hJSlNUVVZXWFlaY2Rl"
        "ZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5"
        "usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhED"
        "EQA/AP0poA//2Q=="
    )
    vec = embed_svc.embed_query(image=tiny_jpeg)
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_no_input(embed_svc):
    """Calling with neither text nor image raises ValueError."""
    with pytest.raises(ValueError, match="At least one"):
        embed_svc.embed_query()
