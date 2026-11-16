from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    """Render/Neon/Heroku provide postgres:// URLs. SQLAlchemy async needs postgresql+psycopg://."""
    url = (url or "").strip()
    if not url:
        return "sqlite+aiosqlite:///./nexusai.db"
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url

database_url = normalize_database_url(settings.database_url)
engine_kwargs = {"echo": False}
if database_url.startswith("postgresql+psycopg://"):
    # Render's internal URL works without TLS; Neon/external URLs often require it.
    # "prefer" succeeds in both cases.
    engine_kwargs["connect_args"] = {"sslmode": "prefer"}

engine = create_async_engine(database_url, **engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
class Base(DeclarativeBase): pass

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_db():
    from app.models import User, Document, AuditLog
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
