from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(title=settings.app_name, version="1.0.0", description="Enterprise RAG, agentic workflows and ML analytics platform")

origins = settings.origins
if origins == ["*"]:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
else:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(router)

static_dir = Path(settings.static_dir)
assets_dir = static_dir / "assets"
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    index = static_dir / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {"name": "NexusAI", "docs": "/docs", "health": "/api/health"}

@app.get("/vite.svg")
async def vite_icon():
    icon = static_dir / "vite.svg"
    if icon.is_file():
        return FileResponse(icon)
    from fastapi import HTTPException
    raise HTTPException(404)
