"""Conexão com SQL Server via pyodbc.

Sem pool próprio: o ODBC Driver Manager já faz pooling de conexões físicas
(pyodbc habilita ``pooling=True`` por padrão), então abrir/fechar uma conexão
lógica por operação é barato e evita a complexidade de um pool caseiro.
``pyodbc`` é importado de forma tardia (dentro das funções) para que módulos
que nunca usam o backend SQL Server (ex.: testes, backend "memory") não
precisem tê-lo instalado.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    import pyodbc

logger = get_logger(__name__)


def _build_connection_string(settings: Settings) -> str:
    parts = [
        f"DRIVER={{{settings.db_driver}}}",
        f"SERVER={settings.db_server}",
        f"DATABASE={settings.db_database}",
        f"Connection Timeout={settings.db_connect_timeout}",
    ]
    if settings.db_trusted_connection:
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={settings.db_username}")
        parts.append(f"PWD={settings.db_password}")
    return ";".join(parts)


def get_connection(settings: Settings | None = None) -> "pyodbc.Connection":
    """Abre uma nova conexão com o SQL Server (autocommit desligado)."""
    import pyodbc

    settings = settings or get_settings()
    connection_string = _build_connection_string(settings)
    return pyodbc.connect(connection_string, autocommit=False)


@contextmanager
def connection_scope(settings: Settings | None = None) -> Iterator["pyodbc.Connection"]:
    """Context manager transacional: commit no caminho feliz, rollback em erro,
    fechamento garantido da conexão."""
    conn = get_connection(settings)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
