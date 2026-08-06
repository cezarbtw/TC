"""Configuração central de logging da aplicação."""
from __future__ import annotations

import logging
import sys

_CONFIGURADO = False
_FORMATO_LOG = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logging(level: int = logging.INFO) -> None:
    """Configura o logging global uma única vez (idempotente)."""
    global _CONFIGURADO
    if _CONFIGURADO:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMATO_LOG))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    _CONFIGURADO = True


def obter_logger(nome: str) -> logging.Logger:
    """Atalho para obter um logger nomeado por módulo."""
    return logging.getLogger(nome)
