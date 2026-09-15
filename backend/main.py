import base64
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.genai.errors import APIError as GeminiAPIError
from groq import APIError as GroqAPIError

from chat_service import ChatService
from config import Settings
from embedding_service import EmbeddingService, UnsupportedImageError
from models import Prestataire, SearchRequest, SearchResult
from seed_data import load_seed_prestataires
from vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

settings = Settings()
embed_svc = EmbeddingService(settings)
vector_store = InMemoryVectorStore()
chat_svc = ChatService(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_seed_prestataires(vector_store, embed_svc)
    yield


app = FastAPI(title="PrestaSearch API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- GET /health ---
@app.get("/health")
async def health():
    return {"status": "ok", "prestataire_count": vector_store.count}


# --- GET /prestataires ---
@app.get("/prestataires", response_model=list[Prestataire])
async def list_prestataires():
    return list(reversed(vector_store.prestataires))


# --- POST /prestataires ---
@app.post("/prestataires", status_code=201)
async def add_prestataire(
    name: str = Form(...),
    specialty: str = Form(...),
    description: str = Form(...),
    services: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    hourly_rate: float = Form(0),
    phone: str = Form(""),
    email: str = Form(""),
    rating: float = Form(0),
    image: UploadFile | None = File(None),
):
    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()

    svc_list = [s.strip() for s in services.split(",") if s.strip()]

    prestataire = Prestataire(
        name=name,
        specialty=specialty,
        description=description,
        services=svc_list,
        city=city,
        country=country,
        hourly_rate=hourly_rate,
        phone=phone,
        email=email,
        rating=rating,
        image_base64=image_base64,
    )

    try:
        embedding = embed_svc.embed_prestataire(prestataire)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    vector_store.add(prestataire, embedding)
    return {"prestataire_id": prestataire.id}


# --- PUT /prestataires/{id} ---
@app.put("/prestataires/{prestataire_id}")
async def update_prestataire(
    prestataire_id: str,
    name: str = Form(...),
    specialty: str = Form(...),
    description: str = Form(...),
    services: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    hourly_rate: float = Form(0),
    phone: str = Form(""),
    email: str = Form(""),
    rating: float = Form(0),
    image: UploadFile | None = File(None),
    keep_image: str = Form("false"),
):
    # Find existing prestataire to preserve fields
    existing = next((p for p in vector_store.prestataires if p.id == prestataire_id), None)
    if not existing:
        raise HTTPException(404, "Prestataire not found")

    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()
    elif keep_image == "true":
        image_base64 = existing.image_base64

    svc_list = [s.strip() for s in services.split(",") if s.strip()]

    prestataire = Prestataire(
        id=prestataire_id,
        name=name,
        specialty=specialty,
        description=description,
        services=svc_list,
        city=city,
        country=country,
        hourly_rate=hourly_rate,
        phone=phone,
        email=email,
        rating=rating,
        image_base64=image_base64,
        created_at=existing.created_at,
    )

    try:
        embedding = embed_svc.embed_prestataire(prestataire)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    vector_store.update(prestataire_id, prestataire, embedding)
    return {"prestataire_id": prestataire_id}


# --- POST /search ---
@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            logger.warning("Unsupported image format: %s", e)
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.error("Image description failed: %s", e)
            raise HTTPException(502, "Image analysis service temporarily unavailable. Please try again shortly.") from e

    try:
        query_embedding = embed_svc.embed_query(
            text=request.text, image_description=image_description
        )
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    return vector_store.search(query_embedding, top_k=settings.TOP_K_RESULTS)


# --- POST /chat ---
@app.post("/chat")
async def chat(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            logger.warning("Unsupported image format: %s", e)
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.error("Image description failed: %s", e)
            raise HTTPException(502, "Image analysis service temporarily unavailable. Please try again shortly.") from e

    try:
        query_embedding = embed_svc.embed_query(
            text=request.text, image_description=image_description
        )
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    results = vector_store.search(query_embedding, top_k=settings.TOP_K_RESULTS)
    user_message = " ".join(filter(None, [request.text, image_description]))

    async def event_stream():
        try:
            async for token in chat_svc.generate_response_stream(
                user_message, results
            ):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except GroqAPIError as e:
            logger.error("Chat generation failed: %s", e)
            yield f"data: [ERROR] Chat service unavailable\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
