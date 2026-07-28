"""Tradução de erros do pyodbc para exceções de domínio."""
from __future__ import annotations

from app.core.errors import PersistenceError
from app.core.logging import get_logger

logger = get_logger(__name__)


def translate_pyodbc_error(exc: Exception) -> PersistenceError:
    """Loga o erro original (com SQLSTATE, se disponível) e devolve uma
    ``PersistenceError`` genérica, sem vazar detalhes internos (query,
    parâmetros, driver) na resposta enviada ao cliente."""
    sqlstate = exc.args[0] if getattr(exc, "args", None) else "desconhecido"
    logger.error("Erro de banco de dados (SQLSTATE=%s): %s", sqlstate, exc, exc_info=exc)
    return PersistenceError()
