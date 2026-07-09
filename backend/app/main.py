"""Ponto de entrada da aplicação FastAPI (app factory).

Execute com:  uvicorn app.main:app --reload   (a partir da pasta backend/)
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API de apoio a consultas psicológicas: detecção de faces e "
            "classificação de emoções (DeepFace + OpenCV)."
        ),
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
