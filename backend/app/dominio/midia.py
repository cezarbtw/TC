"""Entidades relacionadas a mídia (metadados de vídeo)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetadadosVideo:
    """Metadados extraídos de um arquivo de vídeo."""

    fps: float
    total_frames: int
    duracao_segundos: float

    @property
    def rotulo_duracao(self) -> str:
        """Duração no formato ``MM:SS`` (usado pelo dashboard)."""
        total = max(0, int(round(self.duracao_segundos)))
        minutos, segundos = divmod(total, 60)
        return f"{minutos:02d}:{segundos:02d}"
