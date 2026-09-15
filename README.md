# PrestaSearch — Semantic Provider Search

Find the right service provider by describing your need in natural language or by sending a photo. Powered by Gemini (embeddings) and Groq LLaMA (chatbot).

## Stack

- **Backend**: Python 3.12, FastAPI, NumPy (in-memory vector store)
- **Embeddings**: Google Gemini Embedding API (`gemini-embedding-001`, 3072-dim)
- **Vision**: Google Gemini Generative API (`gemini-2.5-flash`) — describes images for multimodal search
- **Chat**: Groq LLaMA 3.3 70B (streamed responses)
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite
- **Infra**: Docker Compose, Nginx (reverse proxy)

## Quick start with Docker

### Prerequisites

- Docker and Docker Compose
- Google API key (Gemini)
- Groq API key

### Steps

```bash
# 1. Clone the project
git clone <repo-url>
cd PrestaSearch

# 2. Configure API keys
cp .env.example .env
# Edit .env with your keys:
#   GOOGLE_API_KEY=your-google-api-key
#   GROQ_API_KEY=your-groq-api-key

# 3. Start the containers
docker compose up --build

# 4. Open http://localhost
```

### Docker architecture

```
┌────────────────┐       ┌────────────────┐
│   frontend     │       │   backend      │
│   (nginx)      │──────>│   (FastAPI)    │
│   port 80      │ /api/ │   port 8000    │
└────────────────┘       └────────────────┘
        │                        │
   static files            .env variables
   React build (dist/)    GOOGLE_API_KEY
                          GROQ_API_KEY
```

- **frontend**: Nginx serves the React build and proxies `/api/*` to the backend
- **backend**: FastAPI + Uvicorn, loads 15 seed providers at startup

### Useful commands

```bash
# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Backend logs only
docker compose logs -f backend

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build
```

---

## Local installation (without Docker)

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google API key (Gemini)
- Groq API key

### 1. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
cp .env backend/.env
```

### 2. Backend

```bash
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --port 8000
```

The server loads 15 providers at startup (~10s), then exposes:

| Method | Route | Description |
|--------|-------|-------------|
| GET | /health | Status + provider count |
| GET | /prestataires | List all providers |
| POST | /prestataires | Add a provider (multipart form) |
| PUT | /prestataires/{id} | Update a provider (multipart form, `keep_image` flag) |
| POST | /search | Semantic search (JSON, text and/or image) |
| POST | /chat | Chat with SSE streaming (text and/or image) |

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dev server proxies API calls to the backend.

---

## Usage

- **Search tab**: Describe your need ("I have a leak under my sink") or send a photo (drag & drop, Ctrl+V, or button). The assistant responds conversationally with the most relevant providers.
- **Admin tab**: Add new providers with name, specialty, description, services, city, hourly rate, and an optional photo. Click the pencil icon on a card to edit an existing provider. Changes are immediately reflected in search.

### Image search — how it works

1. The user sends a photo (accepted formats: any browser `image/*`, max 5 MB)
2. The backend detects the MIME type and sends the image to **Gemini Flash** to get a description in English
3. This description is used to generate the embedding and find the most relevant providers
4. The description is also passed to the LLM (LLaMA 3.3) so it can provide a contextualized response

**Formats supported by Gemini Vision**: JPEG, PNG, WebP, HEIC. Other formats return a 415 error with an explicit message.

## Tests

```bash
cd backend
python -m pytest tests/ -v
```
