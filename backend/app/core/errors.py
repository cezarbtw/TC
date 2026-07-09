"""Exceções de domínio e tradução para respostas HTTP.

As exceções de domínio carregam o status HTTP apropriado, mas não dependem do
FastAPI. O ``register_exception_handlers`` faz a ponte entre elas e a resposta
JSON no formato ``{"detail": ...}`` — exatamente o campo que o interceptor do
frontend (services/api.js) lê para exibir mensagens amigáveis.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class DomainError(Exception):
    """Erro de regra de negócio traduzível para uma resposta HTTP."""

    status_code: int = 400
    message: str = "Requisição inválida."

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class UnsupportedMediaTypeError(DomainError):
    status_code = 415
    message = "Formato de arquivo não suportado."


class FileTooLargeError(DomainError):
    status_code = 413
    message = "Arquivo excede o tamanho máximo permitido."


class InvalidMediaError(DomainError):
    status_code = 422
    message = "Não foi possível ler o arquivo enviado."


class NoFaceDetectedError(DomainError):
    status_code = 422
    message = "Nenhuma face foi detectada no material enviado."


class EmotionAnalysisError(DomainError):
    status_code = 500
    message = "Falha ao processar a análise emocional."


class SessionNotFoundError(DomainError):
    status_code = 404
    message = "Sessão não encontrada."


def register_exception_handlers(app: FastAPI) -> None:
    """Registra os handlers que convertem exceções em respostas JSON."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        # 5xx merece log de erro; 4xx é esperado (warning).
        if exc.status_code >= 500:
            logger.error("Erro de domínio: %s", exc.message, exc_info=exc)
        else:
            logger.warning("Erro de domínio (%s): %s", exc.status_code, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro inesperado", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno ao processar a requisição."},
        )
