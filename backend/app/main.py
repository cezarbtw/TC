"""Ponto de entrada da aplicação FastAPI (app factory).

Execute com:  uvicorn app.main:app --reload   (a partir da pasta backend/)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps.dependencies import warmup_models
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Carrega os modelos de IA uma única vez, no startup, e não a cada requisição.
    try:
        warmup_models()
        logger.info("Modelos de análise emocional carregados na inicialização.")
    except Exception:  # noqa: BLE001 - não impedir o boot por falha de warmup
        logger.exception("Falha ao pré-carregar os modelos; será tentado sob demanda.")
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API de apoio a consultas psicológicas: detecção de faces (YOLOv8) e "
            "classificação de emoções (HSEmotion)."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"], summary="Verificação de saúde")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    logger.info("%s v%s inicializada.", settings.app_name, settings.app_version)
    return app


app = create_app()
