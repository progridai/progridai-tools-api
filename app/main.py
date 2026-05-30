from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.privacy.routes import router as privacy_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ProgridAI Tools API - Ferramentas reutilizáveis de IA"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(privacy_router)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

@app.get("/version", tags=["System"])
def version():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
