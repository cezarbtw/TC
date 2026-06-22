"""
EmotionLens — Back End Principal
FastAPI + DeepFace + SQLite

Uso:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import sessions, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco de dados ao subir a aplicação."""
    init_db()
    yield


app = FastAPI(
    title="EmotionLens API",
    description="API para análise de expressões faciais em vídeos — TCC Ciência da Computação",
    version="1.0.0",
    lifespan=lifespan,
)

# Permite requisições do front end (ajuste a origem conforme necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Em produção: substitua por ["http://localhost:5500"] etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router,   prefix="/api", tags=["Upload"])
app.include_router(sessions.router, prefix="/api", tags=["Sessões"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "EmotionLens API", "version": "1.0.0"}
