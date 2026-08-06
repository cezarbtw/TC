"""Tradução de erros do pyodbc para exceções de domínio."""
from __future__ import annotations

from app.nucleo.erros import ErroPersistencia
from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)


def traduzir_erro_pyodbc(exc: Exception) -> ErroPersistencia:
    """Loga o erro original (com SQLSTATE, se disponível) e devolve um
    ``ErroPersistencia`` genérico, sem vazar detalhes internos (query,
    parâmetros, driver) na resposta enviada ao cliente."""
    sqlstate = exc.args[0] if getattr(exc, "args", None) else "desconhecido"
    logger.error("Erro de banco de dados (SQLSTATE=%s): %s", sqlstate, exc, exc_info=exc)
    return ErroPersistencia()
