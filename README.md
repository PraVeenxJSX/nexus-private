---
title: NexusAI
emoji: 🧠
colorFrom: slate
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
short_description: RAG workspace with FastAPI, Chroma, and React
---

# NexusAI — Autonomous Enterprise Intelligence Platform

A full-stack portfolio project combining a React/TypeScript workspace, FastAPI, LangChain, LangGraph, retrieval-augmented generation (RAG), Chroma vector search, and scikit-learn analytics.

> This is a strong development/portfolio foundation, not a fully audited enterprise production system. Review security, storage, permissions, backups, rate limits and deployment settings before exposing it publicly.

## Features

- Email/password registration and login using JWT.
- Private per-user Chroma collections for document retrieval.
- PDF, DOCX, TXT, Markdown and CSV document ingestion.
- Recursive chunking and local FastEmbed (ONNX) embeddings; no PyTorch required.
- LangChain retrieval and grounded LLM responses with source excerpts.
- LangGraph workflow entry point for the knowledge-research agent.
- CSV profiling, missing-value summary and Isolation Forest anomaly detection.
- Audit events for uploads and chat requests.
- React dashboard, knowledge base, chat workspace, analytics and system health screens.
- Dockerfiles and Docker Compose.

## Architecture

```text
React + TypeScript (Vite)
        | REST + JWT
        v
FastAPI / Pydantic
   |       |        |
   |       |        +--> scikit-learn / pandas analytics
   |       +----------> SQLAlchemy (SQLite dev; PostgreSQL URL supported)
   +------------------> LangGraph workflow
                           |
                        LangChain
                           |
                  Chroma + embeddings
                           |
                   OpenAI Chat Model
```

## Prerequisites

- Python 3.11 recommended (3.12 may work; native ML dependencies can vary by platform).
- Node.js 20 or 22 LTS and npm.
- Git.
- OpenAI API key for hosted LLM answers. Local Hugging Face embeddings download a model on first run. Chat requires `OPENAI_API_KEY` in this starter.
- Optional Docker Desktop.

## Quick start — Windows PowerShell

Open PowerShell in the `nexusai` project folder.

### 1. Backend

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`, set a strong `SECRET_KEY` and your `OPENAI_API_KEY`.

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs  
Health: http://localhost:8000/api/health

### 2. Frontend (new terminal)

```powershell
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Run:

```powershell
npm run dev
```

Open http://localhost:5173. Register an account, upload a document, then ask a question in AI Workspace.

### Linux / macOS backend commands

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend commands are the same (`cd frontend && npm install && npm run dev`).

## Docker

1. Create `backend/.env` from `backend/.env.example` and configure secrets/API key.
2. From the repository root:

```bash
docker compose up --build
```

Frontend: http://localhost:5173 (container serves the compiled app)  
Backend: http://localhost:8000/docs

For a real hosted deployment, change the frontend API URL to your public HTTPS API URL at build time, configure CORS, use managed PostgreSQL/object storage, and put a reverse proxy/TLS in front of the services.

## Deployment — free (Hugging Face Spaces)

This is the recommended **free** host. Hugging Face CPU Spaces have enough RAM for FastEmbed + Chroma. Render’s 512 MB free web plan will OOM this app.

You get **one public URL** that serves both the React UI and the FastAPI backend (`Dockerfile` at the repo root, port **7860**).

### 1. Optional: free PostgreSQL on Neon

SQLite inside the Space works for a quick demo, but data is lost when the Space restarts. For accounts that survive restarts:

1. Create a project at [neon.tech](https://neon.tech) (free tier).
2. Copy the connection string (`postgresql://...` or `postgres://...`).
   The app rewrites it to `postgresql+psycopg://` automatically.

### 2. Create the Space

1. Push this repository to GitHub (including the root `Dockerfile`).
2. Open [huggingface.co/new-space](https://huggingface.co/new-space).
3. Name the Space, set **SDK** to **Docker**, hardware **CPU basic** (free), and make it **public** (required for free hardware).
4. Choose **GitHub** and select `PraVeenxJSX/nexus-private` (or your fork), branch `main`.
5. Wait for the Docker build. First build is slow (Python + Node).

Direct URL after it starts:

```text
https://<your-hf-username>-<space-name>.hf.space
https://<your-hf-username>-<space-name>.hf.space/api/health
```

### 3. Space secrets (Settings → Variables and secrets)

| Secret | Required | Value |
|---|---|---|
| `SECRET_KEY` | Yes | Long random string |
| `NVIDIA_API_KEY` | For NVIDIA chat | Your NVIDIA NIM key |
| `OPENAI_API_KEY` | If `LLM_PROVIDER=openai` | Your OpenAI key |
| `LLM_PROVIDER` | No | `nvidia` (default) or `openai` |
| `DATABASE_URL` | Recommended | Neon URI; omit to use SQLite |
| `CORS_ORIGINS` | No | Not needed when UI and API share the Space |

The Space sleeps after idle time on the free CPU. The first request after sleep can take a minute.

### 4. Optional split: Vercel UI + Hugging Face API

If you only want the API on Hugging Face and the UI on Vercel (both free):

- Space still uses the root `Dockerfile`, or `backend/Dockerfile` with `PORT=7860`.
- Vercel project root: `frontend`
- `VITE_API_URL=https://<your-hf-username>-<space-name>.hf.space`
- Space secret `CORS_ORIGINS=https://your-project.vercel.app`

## Deployment — Render backend + Vercel frontend

Render is **not** a reliable free option for this project (512 MB OOM). Use it only if you pay for at least 2 GB RAM.

This repository is prepared for a split deployment:

- **Backend:** Render web service using `backend/Dockerfile`
- **Frontend:** Vercel using `frontend/` as the project root

### 1. Prepare the backend

This repository includes a [`render.yaml`](./render.yaml) Blueprint. In Render,
choose **New > Blueprint**, connect the GitHub repository, and apply the
Blueprint. It configures:

- Docker context: `backend`
- Dockerfile: `backend/Dockerfile`
- Port: `8000` (Render also injects `PORT`)
- Health check: `/api/health`
- A generated `SECRET_KEY`
- A managed PostgreSQL instance, with `DATABASE_URL` wired automatically
  (`postgres://...` is converted to `postgresql+psycopg://...` at runtime)
- Web service plan `1c-2g` (2 GB RAM) is recommended. The API can boot on
  Render's 512 MB free web plan because embeddings use FastEmbed (ONNX), not
  PyTorch. If logs show `Out of memory (used over 512Mi)` or `No open ports
  detected`, raise the instance to 2 GB in **Settings → Instance Type**.

When Render prompts for environment values, provide:

- `NVIDIA_API_KEY` or `OPENAI_API_KEY`
- `CORS_ORIGINS`, initially `http://localhost:5173`

The backend exposes its health check at `/api/health`. After deployment, verify:

```text
https://your-render-api-url.onrender.com/api/health
```

If the deploy fails with a database dialect error, confirm `DATABASE_URL` is set
and that you redeployed after the SQLAlchemy URL conversion in
`backend/app/core/database.py`. If it fails with Out of Memory, raise the
instance to at least 2 GB.

### 2. Deploy the frontend to Vercel

Import the repository into Vercel and set:

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment variable:
  `VITE_API_URL=https://your-render-api-url.onrender.com`

`VITE_API_URL` is a build-time variable. Redeploy the frontend after changing it.

### 3. Complete CORS configuration

After Vercel provides the final production URL, update the Render backend's
`CORS_ORIGINS` environment variable to that exact URL and redeploy the backend.
For a temporary preview deployment, list multiple comma-separated origins.

### Storage warning

The current application writes SQLite data, uploaded documents, and Chroma data
to local container paths. These are suitable for a demo but should not be treated
as durable production storage. Use managed PostgreSQL and durable object/vector
storage before relying on uploaded documents or user data across container
rebuilds.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `APP_NAME` | No | API title |
| `ENVIRONMENT` | No | Environment label |
| `SECRET_KEY` | Yes for secure deployment | JWT signing secret; replace default |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT expiry |
| `DATABASE_URL` | No | SQLAlchemy URL; defaults to local SQLite |
| `OPENAI_API_KEY` | For chat | OpenAI API key; never commit it |
| `OPENAI_MODEL` | No | Chat model name, default `gpt-4o-mini` |
| `EMBEDDING_MODEL` | No | Local Sentence Transformers embedding model |
| `VECTOR_STORE_PATH` | No | Persistent Chroma directory |
| `UPLOAD_DIR` | No | Uploaded source files |
| `MAX_UPLOAD_MB` | No | Upload size limit |
| `CORS_ORIGINS` | No | Comma-separated allowed frontend origins |
| `VITE_API_URL` | Frontend | API base URL, default `http://localhost:8000` |

### Generate a secure SECRET_KEY

PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Linux/macOS:
```bash
python -c 'import secrets; print(secrets.token_urlsafe(48))'
```

## API endpoints

All authenticated endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Auth | Description |
|---|---|---:|---|
| GET | `/` | No | Service metadata |
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/register` | No | Create account; JSON `{ "email": "you@example.com", "password": "minimum8chars" }` |
| POST | `/api/auth/login` | No | Login; returns JWT |
| GET | `/api/auth/me` | Yes | Current user |
| POST | `/api/documents/upload` | Yes | Multipart field `file`; PDF/DOCX/TXT/MD/CSV |
| GET | `/api/documents` | Yes | List current user's documents |
| POST | `/api/chat` | Yes | JSON `{ "question": "What does the policy say?" }` |
| POST | `/api/analytics/csv` | Yes | Multipart field `file`; CSV profile + anomaly results |

Swagger UI at `/docs` lets you register, authorize, and try the APIs.

## Example API calls

Register:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"ChangeThis123"}'
```
Upload (replace TOKEN and path):
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H 'Authorization: Bearer TOKEN' \
  -F 'file=@./company-policy.pdf'
```
Ask:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Authorization: Bearer TOKEN' -H 'Content-Type: application/json' \
  -d '{"question":"Summarize the leave policy and cite the source."}'
```

## Where to get API keys / services

- OpenAI API key: https://platform.openai.com/api-keys (API billing is separate from a ChatGPT subscription).
- OpenAI model/pricing information: https://platform.openai.com/docs/models and https://openai.com/api/pricing/.
- No key required for local Sentence Transformers embeddings; first use downloads model weights from Hugging Face.
- Optional PostgreSQL: https://www.postgresql.org/download/.
- Optional Docker Desktop: https://www.docker.com/products/docker-desktop/.
- No separate LangChain, LangGraph, Chroma or scikit-learn API key is required.

## Important implementation notes / current scope

- Chroma is the active vector store. User-specific collection names are used, and uploaded document metadata includes the owner ID. This starter's Chroma isolation is application-level; production deployments should add stronger tenant isolation, storage encryption and authorization tests.
- SQL defaults to SQLite for quick local setup. The SQLAlchemy URL can be changed to PostgreSQL after adding a compatible async PostgreSQL driver and configuring a managed database.
- The LangGraph workflow currently has a single knowledge-research node. Extend it with planner, SQL analyst, report writer, approval and tool-execution nodes as follow-on milestones.
- CSV analytics uses Isolation Forest and descriptive statistics. Treat anomaly flags as investigation candidates, not proof of fraud or business errors.
- Chat uses OpenAI Chat Completions via LangChain. The selected model must be available to your API account; model availability and pricing can change.
- Document uploads are stored locally. Add object storage, virus scanning, retention controls and deletion workflows before production use.
- Add tests, rate limiting, refresh/revocation tokens, password reset, tenant-level permission tests, and robust audit redaction before public deployment.

## Suggested next engineering milestones

1. Add PostgreSQL + pgvector as an alternative vector backend and Alembic migrations.
2. Implement BM25 + dense hybrid retrieval and a cross-encoder reranker.
3. Add evaluation datasets and RAG metrics (Recall@K, MRR, faithfulness, answer relevancy) with Ragas/DeepEval.
4. Expand LangGraph into planner → retrieval/SQL/tools → verifier → human approval → report nodes.
5. Add streaming chat, conversation persistence and document version/deletion support.
6. Add LangSmith/Langfuse tracing, MLflow experiment tracking and Prometheus metrics.
7. Add RBAC, tenant isolation, prompt-injection defenses, upload scanning and integration tests.

## License

MIT (see LICENSE).


## NVIDIA Nemotron configuration

NexusAI defaults to NVIDIA NIM using the OpenAI-compatible endpoint.
Set `LLM_PROVIDER=nvidia`, `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, and
`NVIDIA_MODEL` in `backend/.env`. The default model is
`nvidia/nemotron-3-ultra-550b-a55b`.

Embeddings are generated locally with FastEmbed (ONNX MiniLM) and do not use
the NVIDIA chat-completion key. The first embedding-model run downloads model
weights, so it needs internet access and local disk space.

To use OpenAI instead, set `LLM_PROVIDER=openai` and configure
`OPENAI_API_KEY` and `OPENAI_MODEL`.
