"""Entidades e vocabulário do domínio de emoções.

Camada pura: sem dependência de FastAPI, do modelo de IA ou de OpenCV. Define os
rótulos canônicos (em inglês) e o mapeamento para o português usado pelo frontend.
"""
from __future__ import annotations

from dataclasses import dataclass

# Rótulos canônicos de emoção (7 classes).
EN_EMOTIONS: tuple[str, ...] = (
    "angry",
    "disgust",
    "fear",
    "happy",
    "sad",
    "surprise",
    "neutral",
)

# Rótulos em português na MESMA ordem/conjunto usada pelo frontend
# (frontend/src/utils/constants.js -> EMOTION_KEYS).
PT_EMOTIONS: tuple[str, ...] = (
    "feliz",
    "triste",
    "raiva",
    "surpresa",
    "medo",
    "nojo",
    "neutro",
)

# Tradução rótulo canônico (EN) -> frontend (PT).
EN_TO_PT: dict[str, str] = {
    "happy": "feliz",
    "sad": "triste",
    "angry": "raiva",
    "surprise": "surpresa",
    "fear": "medo",
    "disgust": "nojo",
    "neutral": "neutro",
}


# Índice inverso PT -> EN (usado na tradução de scores).
_PT_TO_EN: dict[str, str] = {pt: en for en, pt in EN_TO_PT.items()}


def translate_scores_to_pt(en_scores: dict[str, float]) -> dict[str, float]:
    """Converte um dicionário de scores em inglês para chaves em português.

    Garante que todas as sete emoções em português estejam presentes (0.0 quando
    ausentes), preservando a ordem esperada pelo frontend (PT_EMOTIONS).
    """
    return {
        pt: float(en_scores.get(_PT_TO_EN[pt], 0.0)) for pt in PT_EMOTIONS
    }


@dataclass(frozen=True)
class FaceRegion:
    """Bounding box de uma face detectada, em pixels."""

    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return max(0, self.w) * max(0, self.h)


@dataclass(frozen=True)
class FaceEmotion:
    """Resultado da classificação emocional de uma única face.

    ``scores`` usa os rótulos canônicos em inglês (0..100). ``confidence`` é a
    confiança da emoção predominante; ``detection_confidence`` é a confiança do
    detector de faces (YOLOv8) na existência da face.
    """

    scores: dict[str, float]
    dominant: str
    confidence: float
    region: FaceRegion | None = None
    detection_confidence: float = 1.0
