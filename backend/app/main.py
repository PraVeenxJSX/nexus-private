from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(title=settings.app_name, version="1.0.0", description="Enterprise RAG, agentic workflows and ML analytics platform")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
@app.on_event("startup")
async def startup(): await init_db()
@app.get("/")
async def root(): return {"name":"NexusAI", "docs":"/docs", "health":"/api/health"}
