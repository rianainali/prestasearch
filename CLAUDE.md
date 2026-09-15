# PrestaSearch — Plateforme de Recherche Sémantique de Prestataires

## Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | Python 3.12 / FastAPI + Uvicorn | API REST + service orchestration |
| Embedding | Gemini Embedding API (`gemini-embedding-001`) | 3072-dim vectors (text-only) |
| Vision | Gemini Generative API (`gemini-2.5-flash`) | Image → text description for multimodal search |
| Vector store | In-memory NumPy | Cosine similarity, matrix shape (N, 3072) |
| LLM chatbot | Groq — LLaMA 3.3 70B (`llama-3.3-70b-versatile`) | Streamed conversational responses |
| Frontend | React 18 + TypeScript + TailwindCSS + Vite | Chat UI + provider form (add & edit) |
| Infra | Docker Compose + Nginx | Frontend served by nginx, proxies /api to backend |

## Project structure

```
PrestaSearch/
├── backend/
│   ├── config.py                # Settings (pydantic-settings, reads .env)
│   ├── models.py                # Prestataire, SearchResult, SearchRequest
│   ├── embedding_service.py     # EmbeddingService (Gemini)
│   ├── vector_store.py          # InMemoryVectorStore (NumPy)
│   ├── chat_service.py          # ChatService (Groq)
│   ├── seed_data.py             # SEED_PRESTATAIRES (15 items) + load_seed_prestataires()
│   ├── main.py                  # FastAPI app + lifespan + all routes
│   ├── Dockerfile               # Python 3.12-slim, context = project root
│   └── tests/
│       ├── test_embedding.py    # 4 tests
│       ├── test_vector_store.py # 3 tests
│       ├── test_api.py          # 5 tests
│       └── test_chat_service.py # 4 tests
├── frontend/
│   ├── Dockerfile               # Multi-stage: Node build → Nginx serve
│   ├── nginx.conf               # Proxy /api/* → backend:8000, serve SPA
│   └── src/
│       ├── components/
│       │   ├── ChatInterface.tsx # Chat UI: drag&drop, paste (Ctrl+V), streaming, provider cards
│       │   ├── ProviderForm.tsx  # Add prestataire form with validation
│       │   ├── ProviderCard.tsx  # Provider card with score color coding
│       │   └── ImageUploader.tsx # Drag & drop image with preview (used in ProviderForm)
│       ├── services/
│       │   ├── api.ts           # HTTP calls (getPrestataires, addPrestataire, searchPrestataires)
│       │   └── chatStream.ts    # SSE streaming client
│       ├── types/
│       │   └── index.ts         # TS types mirroring Pydantic models
│       └── App.tsx              # Main layout with Recherche/Admin tabs
├── frontend/e2e/
│   └── presta-search.spec.ts   # 4 Playwright E2E tests
├── docker-compose.yml           # backend (port 8000) + frontend/nginx (port 80)
├── .env.example                 # Environment variable template
├── .env                         # API keys (gitignored)
├── requirements.txt             # Python dependencies
└── CLAUDE.md                    # This file
```

## Data model

### Prestataire
- `id` (UUID4), `name`, `specialty`, `description`, `services` (list[str])
- `city`, `country`, `hourly_rate`, `phone`, `email`, `rating` (0-5)
- `image_base64`, `created_at`

### SearchResult
- `prestataire` (Prestataire) + `similarity_score` (0.0-1.0)

### SearchRequest
- `text` (optional) + `image_base64` (optional)

## API endpoints

- `GET /health` -> `{"status": "ok", "prestataire_count": N}`
- `GET /prestataires` -> all prestataires (reverse chronological)
- `POST /prestataires` (multipart/form-data) -> 201 + `{"prestataire_id": "..."}`
- `PUT /prestataires/{id}` (multipart/form-data, with `keep_image` flag) -> `{"prestataire_id": "..."}`
- `POST /search` (JSON `{text?, image_base64?}`) -> `list[SearchResult]` top-K
- `POST /chat` (JSON `{text?, image_base64?}`) -> SSE stream (token-by-token)
- Empty search/chat requests return 422
- Unsupported image format returns 415 with French message
- Vision/embedding service errors return 502 with French message

## Seed data

15 prestataires across 7 categories:
- **BTP** (3): Plombier, Électricien, Peintre
- **Beauté** (2): Coiffeuse, Esthéticienne
- **Auto** (2): Mécanicien, Carrossier
- **IT** (2): Développeur web, Dépannage informatique
- **Santé** (2): Kinésithérapeute, Infirmier à domicile
- **Maison** (2): Ménage, Jardinier
- **Divers** (2): Photographe, Professeur particulier

## Code conventions

- Language: code, variable names in **English**; UI labels in **French**
- Backend: Python 3.12, type hints everywhere, Pydantic models for data validation
- Formatting: double quotes for strings, 4-space indentation
- Imports: stdlib first, then third-party, then local (separated by blank lines)
- Tests: pytest, files prefixed with `test_`, fixtures for shared setup
- SDK: using `google-genai` package (not `google-generativeai`) — import as `from google import genai`
- Frontend: React functional components, hooks, TypeScript strict mode
- Styling: TailwindCSS utility classes only (no custom CSS)
- API proxy: frontend dev server proxies `/api/*` -> `http://localhost:8000/`

## How to run

```bash
# Docker (recommended)
cp .env.example .env   # edit with your API keys
docker compose up --build
# Open http://localhost

# Local dev
cd backend && python -m uvicorn main:app --port 8000
cd frontend && npm run dev
# Open http://localhost:5173
```

## Key technical notes

| Topic | Detail |
|-------|--------|
| Embedding model | `gemini-embedding-001` (3072-dim vectors, text-only) |
| Vision model | `gemini-2.5-flash` (used to describe images for multimodal search) |
| SDK | `google-genai` (not `google-generativeai`) |
| Image search flow | Image → Gemini Flash describes it in French → description is embedded + passed to LLM as context |
| Image MIME detection | Backend auto-detects JPEG/PNG/WebP/GIF/BMP/TIFF/HEIC from magic bytes |
| Supported by Gemini Vision | JPEG, PNG, WebP, HEIC (others return 415 with French error message) |
| Rate limiting | Exponential backoff (2s/4s/8s) on 429 and 503 errors |
| Docker | backend Dockerfile context = project root (needs requirements.txt) |
| Nginx proxy | `/api/` → `http://backend:8000/` with SSE buffering disabled |
| Frontend image upload | `image/*` accept attribute (all browser-supported formats), 5MB max |
