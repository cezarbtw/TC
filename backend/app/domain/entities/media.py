"""Entidades relacionadas a mídia (metadados de vídeo)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoMetadata:
    """Metadados extraídos de um arquivo de vídeo."""

    fps: float
    total_frames: int
    duration_seconds: float

    @property
    def duration_label(self) -> str:
        """Duração no formato ``MM:SS`` (usado pelo dashboard)."""
        total = max(0, int(round(self.duration_seconds)))
        minutes, seconds = divmod(total, 60)
        return f"{minutes:02d}:{seconds:02d}"
