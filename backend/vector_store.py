import numpy as np

from models import Prestataire, SearchResult


class InMemoryVectorStore:
    def __init__(self):
        self.vectors: np.ndarray | None = None
        self.prestataires: list[Prestataire] = []

    @property
    def count(self) -> int:
        return len(self.prestataires)

    def add(self, prestataire: Prestataire, embedding: np.ndarray) -> None:
        embedding = embedding.reshape(1, -1)
        if self.vectors is None:
            self.vectors = embedding
        else:
            self.vectors = np.vstack([self.vectors, embedding])
        self.prestataires.append(prestataire)

    def update(
        self, prestataire_id: str, prestataire: Prestataire, embedding: np.ndarray
    ) -> bool:
        for i, p in enumerate(self.prestataires):
            if p.id == prestataire_id:
                self.prestataires[i] = prestataire
                self.vectors[i] = embedding.reshape(-1)
                return True
        return False

    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> list[SearchResult]:
        if self.vectors is None or len(self.prestataires) == 0:
            return []

        scores = self.vectors @ query_embedding
        k = min(top_k, len(self.prestataires))
        top_indices = np.argsort(scores)[::-1][:k]

        return [
            SearchResult(
                prestataire=self.prestataires[i],
                similarity_score=float(np.clip(scores[i], 0.0, 1.0)),
            )
            for i in top_indices
        ]
