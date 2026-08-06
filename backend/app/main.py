"""Ponto de entrada da aplicação FastAPI (app factory).

Execute com:  uvicorn app.main:app --reload   (a partir da pasta backend/)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.nucleo.configuracoes import obter_configuracoes
from app.nucleo.erros import registrar_manipuladores_excecao
from app.nucleo.logs import configurar_logging, obter_logger
from app.rotas.dependencias import aquecer_modelos
from app.rotas.roteador import roteador_api

logger = obter_logger(__name__)


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    # Carrega os modelos de IA uma única vez, no startup, e não a cada requisição.
    try:
        aquecer_modelos()
        logger.info("Modelos de análise emocional carregados na inicialização.")
    except Exception:  # noqa: BLE001 - não impedir o boot por falha de warmup
        logger.exception("Falha ao pré-carregar os modelos; será tentado sob demanda.")
    yield


def criar_app() -> FastAPI:
    configurar_logging()
    configuracoes = obter_configuracoes()

    app = FastAPI(
        title=configuracoes.nome_app,
        version=configuracoes.versao_app,
        description=(
            "API de apoio a consultas psicológicas: detecção de faces (YOLOv8) e "
            "classificação de emoções (HSEmotion)."
        ),
        lifespan=ciclo_de_vida,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuracoes.origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_manipuladores_excecao(app)
    app.include_router(roteador_api)

    @app.get("/health", tags=["health"], summary="Verificação de saúde")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": configuracoes.nome_app}

    logger.info("%s v%s inicializada.", configuracoes.nome_app, configuracoes.versao_app)
    return app


app = criar_app()
