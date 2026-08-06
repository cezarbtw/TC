"""Exceções de domínio e tradução para respostas HTTP.

As exceções de domínio carregam o status HTTP apropriado, mas não dependem do
FastAPI. O ``registrar_manipuladores_excecao`` faz a ponte entre elas e a
resposta JSON no formato ``{"detail": ...}`` — exatamente o campo que o
interceptor do frontend (services/api.js) lê para exibir mensagens amigáveis.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)


class ErroDominio(Exception):
    """Erro de regra de negócio traduzível para uma resposta HTTP."""

    status_code: int = 400
    message: str = "Requisição inválida."

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class TipoMidiaNaoSuportadoError(ErroDominio):
    status_code = 415
    message = "Formato de arquivo não suportado."


class ArquivoMuitoGrandeError(ErroDominio):
    status_code = 413
    message = "Arquivo excede o tamanho máximo permitido."


class MidiaInvalidaError(ErroDominio):
    status_code = 422
    message = "Não foi possível ler o arquivo enviado."


class NenhumaFaceDetectadaError(ErroDominio):
    status_code = 422
    message = "Nenhuma face foi detectada no material enviado."


class ErroAnaliseEmocional(ErroDominio):
    status_code = 500
    message = "Falha ao processar a análise emocional."


class SessaoNaoEncontradaError(ErroDominio):
    status_code = 404
    message = "Sessão não encontrada."


class ErroPersistencia(ErroDominio):
    status_code = 503
    message = "Falha ao acessar a base de dados."


def registrar_manipuladores_excecao(app: FastAPI) -> None:
    """Registra os handlers que convertem exceções em respostas JSON."""

    @app.exception_handler(ErroDominio)
    async def _tratar_erro_dominio(_: Request, exc: ErroDominio) -> JSONResponse:
        # 5xx merece log de erro; 4xx é esperado (warning).
        if exc.status_code >= 500:
            logger.error("Erro de domínio: %s", exc.message, exc_info=exc)
        else:
            logger.warning("Erro de domínio (%s): %s", exc.status_code, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def _tratar_erro_inesperado(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro inesperado", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno ao processar a requisição."},
        )
