import base64
import logging

import numpy as np
from google import genai
from google.genai import types

from config import Settings
from models import Prestataire

logger = logging.getLogger(__name__)

IMAGE_DESCRIBE_PROMPT = (
    "Describe this image in a few sentences in English. "
    "Focus on what service or trade it relates to (e.g. plumbing, gardening, "
    "hairdressing, car repair, etc.). Be concise."
)

SUPPORTED_FORMATS_LABEL = "JPEG, PNG, WebP or HEIC"


class UnsupportedImageError(Exception):
    """Raised when the image format is not supported by the vision model."""
    pass


class EmbeddingService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
        self.model = self.settings.EMBEDDING_MODEL
        self.vision_model = self.settings.VISION_MODEL

    def _build_prestataire_text(self, prestataire: Prestataire) -> str:
        parts = [
            prestataire.name,
            prestataire.specialty,
            prestataire.description,
            ", ".join(prestataire.services),
        ]
        if prestataire.city:
            parts.append(f"City: {prestataire.city}")
        if prestataire.hourly_rate > 0:
            parts.append(f"Rate: {prestataire.hourly_rate}/h")
        return " | ".join(parts)

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _embed(self, parts: list[types.Part]) -> np.ndarray:
        content = types.Content(parts=parts)
        response = self.client.models.embed_content(
            model=self.model,
            contents=content,
        )
        vector = np.array(response.embeddings[0].values, dtype=np.float32)
        return self._normalize(vector)

    def embed_prestataire(self, prestataire: Prestataire) -> np.ndarray:
        text = self._build_prestataire_text(prestataire)
        parts: list[types.Part] = [types.Part.from_text(text=text)]

        if prestataire.image_base64:
            image_bytes = base64.b64decode(prestataire.image_base64)
            parts.append(
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            )

        return self._embed(parts)

    @staticmethod
    def _detect_mime_type(image: bytes) -> str:
        if image[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        if image[:2] == b'\xff\xd8':
            return "image/jpeg"
        if image[:4] == b'RIFF' and image[8:12] == b'WEBP':
            return "image/webp"
        if image[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        if image[:2] == b'BM':
            return "image/bmp"
        if image[:4] in (b'II*\x00', b'MM\x00*'):
            return "image/tiff"
        if len(image) >= 12 and image[4:12] in (
            b'ftypheic', b'ftypheix', b'ftyphevc', b'ftypheim',
            b'ftypheis', b'ftyphevm', b'ftyphevs', b'ftypmif1',
        ):
            return "image/heic"
        return "image/jpeg"

    def describe_image(self, image: bytes, max_retries: int = 3) -> str:
        """Use Gemini generative model to describe an image."""
        import time
        mime_type = self._detect_mime_type(image)
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.vision_model,
                    contents=[
                        types.Content(parts=[
                            types.Part.from_text(text=IMAGE_DESCRIBE_PROMPT),
                            types.Part.from_bytes(data=image, mime_type=mime_type),
                        ])
                    ],
                )
                description = response.text.strip()
                logger.info("Image description: %s", description)
                return description
            except Exception as e:
                err_str = str(e)
                err_lower = err_str.lower()
                is_unsupported = (
                    "invalid_argument" in err_lower
                    or "unable to process input image" in err_lower
                    or "unsupported" in err_lower and "mime" in err_lower
                )
                if is_unsupported:
                    raise UnsupportedImageError(
                        f"Unsupported image format. Please use: {SUPPORTED_FORMATS_LABEL}."
                    ) from e
                is_retryable = "429" in err_str or "503" in err_str or "UNAVAILABLE" in err_str
                if is_retryable and attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Image description failed (%s), retrying in %ds...", err_str[:80], wait)
                    time.sleep(wait)
                else:
                    raise
        return ""

    def embed_query(
        self, text: str | None = None, image_description: str | None = None
    ) -> np.ndarray:
        if not text and not image_description:
            raise ValueError("At least one of text or image_description must be provided")

        query_text = " ".join(filter(None, [text, image_description]))
        parts: list[types.Part] = [types.Part.from_text(text=query_text)]

        return self._embed(parts)
