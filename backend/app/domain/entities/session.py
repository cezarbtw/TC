"""Entidade de rascunho de sessão.

``SessionDraft`` representa uma sessão já analisada, porém ainda sem identidade
persistida (``id``/``name``), que é atribuída pelo repositório. Mantém a regra de
negócio independente da forma de persistência.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionDraft:
    source_file: str
    date: str
    duration: str
    frames: int
    predominant: str
    confidence: float
    probabilities: dict[str, float]
    timeline: dict[str, list[float]]
