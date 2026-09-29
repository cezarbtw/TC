"""Entidade mínima do usuário autenticado."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str
    nome_exibicao: str
    ativo: bool
