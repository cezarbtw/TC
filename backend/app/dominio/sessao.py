"""Entidades de sessão.

``RascunhoSessao`` representa uma sessão já analisada, porém ainda sem
identidade persistida (``id``/``nome``), atribuída pelo repositório.
``Sessao`` é a entidade persistida, retornada pela camada de persistência.

Ambas são dataclasses puras, sem dependência de Pydantic/FastAPI — o
mapeamento para o contrato de API (``SessaoSchema``) acontece explicitamente
na camada de serviços (``app.servicos.servico_sessao``).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RascunhoSessao:
    arquivo_origem: str
    data: str
    duracao: str
    frames: int
    predominante: str
    confianca: float
    probabilidades: dict[str, float]
    linha_do_tempo: dict[str, list[float]]


@dataclass(frozen=True)
class Sessao:
    id: int
    nome: str
    arquivo_origem: str
    data: str
    duracao: str
    frames: int
    predominante: str
    confianca: float
    probabilidades: dict[str, float]
    linha_do_tempo: dict[str, list[float]]
