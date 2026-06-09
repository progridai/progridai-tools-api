from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.privacy.routes import router as privacy_router
from app.modules.auditoria.routes import router as auditoria_router

from contextlib import asynccontextmanager
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas do banco de dados na inicialização
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ProgridAI Tools API - Ferramentas reutilizáveis de IA",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(privacy_router)
app.include_router(auditoria_router, prefix="/auditoria", tags=["Auditoria"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

@app.get("/version", tags=["System"])
def version():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
