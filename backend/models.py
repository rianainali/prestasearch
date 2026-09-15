from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class Prestataire(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(max_length=100)
    specialty: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    services: list[str] = []
    city: str = Field(max_length=100, default="")
    country: str = Field(max_length=100, default="")
    hourly_rate: float = Field(ge=0, default=0)
    phone: str = Field(max_length=20, default="")
    email: str = Field(max_length=200, default="")
    rating: float = Field(ge=0, le=5, default=0)
    image_base64: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SearchResult(BaseModel):
    prestataire: Prestataire
    similarity_score: float = Field(ge=0.0, le=1.0)


class SearchRequest(BaseModel):
    text: str | None = None
    image_base64: str | None = None
