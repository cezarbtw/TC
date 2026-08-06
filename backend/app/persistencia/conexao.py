"""Conexão com SQL Server via pyodbc.

Sem pool próprio: o ODBC Driver Manager já faz pooling de conexões físicas
(pyodbc habilita ``pooling=True`` por padrão), então abrir/fechar uma conexão
lógica por operação é barato e evita a complexidade de um pool caseiro.
``pyodbc`` é importado de forma tardia (dentro das funções) para que módulos
que nunca usam o SQL Server (ex.: testes) não precisem tê-lo instalado.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.nucleo.logs import obter_logger

if TYPE_CHECKING:
    import pyodbc

logger = obter_logger(__name__)


def _construir_string_conexao(configuracoes: Configuracoes) -> str:
    partes = [
        f"DRIVER={{{configuracoes.db_driver}}}",
        f"SERVER={configuracoes.db_servidor}",
        f"DATABASE={configuracoes.db_banco}",
        f"Connection Timeout={configuracoes.db_tempo_limite_conexao}",
    ]
    if configuracoes.db_conexao_confiavel:
        partes.append("Trusted_Connection=yes")
    else:
        partes.append(f"UID={configuracoes.db_usuario}")
        partes.append(f"PWD={configuracoes.db_senha}")
    return ";".join(partes)


def obter_conexao(configuracoes: Configuracoes | None = None) -> "pyodbc.Connection":
    """Abre uma nova conexão com o SQL Server (autocommit desligado)."""
    import pyodbc

    configuracoes = configuracoes or obter_configuracoes()
    string_conexao = _construir_string_conexao(configuracoes)
    return pyodbc.connect(string_conexao, autocommit=False)


@contextmanager
def escopo_conexao(configuracoes: Configuracoes | None = None) -> Iterator["pyodbc.Connection"]:
    """Context manager transacional: commit no caminho feliz, rollback em erro,
    fechamento garantido da conexão."""
    conn = obter_conexao(configuracoes)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
