import os, uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.database import get_db
from app.core.config import settings
from app.core.security import current_user, hash_password, verify_password, create_access_token
from app.models import User, Document, AuditLog
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, ChatIn, ChatOut

router = APIRouter(prefix="/api")
@router.post("/auth/register", response_model=TokenOut)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(409, "Email already registered")
    user = User(email=data.email.lower(), hashed_password=hash_password(data.password))
    db.add(user); await db.commit(); await db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "user": user}
@router.post("/auth/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.hashed_password): raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_access_token(str(user.id)), "user": user}
@router.get("/auth/me", response_model=UserOut)
async def me(user: User = Depends(current_user)): return user

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    allowed = {".pdf", ".txt", ".md", ".docx", ".csv"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed: raise HTTPException(415, "Supported formats: PDF, TXT, MD, DOCX, CSV")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, "File exceeds upload limit")
    os.makedirs(settings.upload_dir, exist_ok=True)
    stored = str(Path(settings.upload_dir) / f"{uuid.uuid4().hex}{ext}")
    with open(stored, "wb") as f: f.write(data)
    try:
        if ext == ".pdf": text = "\n".join(p.extract_text() or "" for p in PdfReader(stored).pages)
        elif ext == ".docx": text = "\n".join(p.text for p in DocxDocument(stored).paragraphs)
        else: text = data.decode("utf-8-sig", errors="replace")
        if not text.strip(): raise ValueError("No extractable text found")
        from app.services.rag import ingest_text
        count = ingest_text(text, file.filename or "uploaded-file", user.id)
        doc = Document(filename=file.filename or "uploaded-file", stored_path=stored, content_type=file.content_type or "application/octet-stream", chunks=count, status="indexed", owner_id=user.id)
    except Exception as exc:
        doc = Document(filename=file.filename or "uploaded-file", stored_path=stored, content_type=file.content_type or "application/octet-stream", chunks=0, status=f"failed: {str(exc)[:150]}", owner_id=user.id)
    db.add(doc); db.add(AuditLog(user_id=user.id, action="document_upload", details=file.filename or "")); await db.commit(); await db.refresh(doc)
    if doc.status != "indexed": raise HTTPException(500, doc.status)
    return {"id": doc.id, "filename": doc.filename, "chunks": doc.chunks, "status": doc.status}

@router.get("/documents")
async def list_documents(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    docs = (await db.scalars(select(Document).where(Document.owner_id == user.id).order_by(Document.created_at.desc()))).all()
    return [{"id":d.id,"filename":d.filename,"chunks":d.chunks,"status":d.status,"created_at":d.created_at} for d in docs]

@router.post("/chat", response_model=ChatOut)
async def chat(data: ChatIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    try:
        from app.services.agents import run_agent
        result = run_agent(data.question, user.id)
        db.add(AuditLog(user_id=user.id, action="rag_chat", details=data.question[:500])); await db.commit()
        return {"answer": result["answer"], "sources": result["sources"], "conversation_id": data.conversation_id}
    except RuntimeError as exc: raise HTTPException(503, str(exc))
    except Exception as exc: raise HTTPException(500, f"AI request failed: {str(exc)[:250]}")

@router.post("/analytics/csv")
async def csv_analytics(file: UploadFile = File(...), user: User = Depends(current_user)):
    if Path(file.filename or "").suffix.lower() != ".csv": raise HTTPException(415, "Upload a CSV file")
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = str(Path(settings.upload_dir) / f"analytics_{uuid.uuid4().hex}.csv")
    with open(path, "wb") as f: f.write(await file.read())
    try:
        from app.services.analytics import analyze_csv
        return analyze_csv(path)
    except Exception as exc: raise HTTPException(400, f"Could not analyze CSV: {str(exc)[:200]}")

@router.get("/health")
async def health(): return {"status":"ok", "service":"NexusAI API"}
