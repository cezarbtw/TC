"""Entidades e vocabulário do domínio de emoções.

Camada pura: sem dependência de FastAPI, do modelo de IA ou de OpenCV. Define
os rótulos canônicos (em inglês) e o mapeamento para o português usado pelo
frontend.
"""
from __future__ import annotations

from dataclasses import dataclass

# Rótulos canônicos de emoção (7 classes).
EMOCOES_EN: tuple[str, ...] = (
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
EMOCOES_PT: tuple[str, ...] = (
    "feliz",
    "triste",
    "raiva",
    "surpresa",
    "medo",
    "nojo",
    "neutro",
)

# Tradução rótulo canônico (EN) -> frontend (PT).
EN_PARA_PT: dict[str, str] = {
    "happy": "feliz",
    "sad": "triste",
    "angry": "raiva",
    "surprise": "surpresa",
    "fear": "medo",
    "disgust": "nojo",
    "neutral": "neutro",
}


# Índice inverso PT -> EN (usado na tradução de scores).
_PT_PARA_EN: dict[str, str] = {pt: en for en, pt in EN_PARA_PT.items()}


def traduzir_scores_para_pt(scores_en: dict[str, float]) -> dict[str, float]:
    """Converte um dicionário de scores em inglês para chaves em português.

    Garante que todas as sete emoções em português estejam presentes (0.0
    quando ausentes), preservando a ordem esperada pelo frontend
    (``EMOCOES_PT``).
    """
    return {
        pt: float(scores_en.get(_PT_PARA_EN[pt], 0.0)) for pt in EMOCOES_PT
    }


@dataclass(frozen=True)
class RegiaoFace:
    """Bounding box de uma face detectada, em pixels."""

    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return max(0, self.w) * max(0, self.h)


@dataclass(frozen=True)
class EmocaoFace:
    """Resultado da classificação emocional de uma única face.

    ``pontuacoes`` usa os rótulos canônicos em inglês (0..100).
    ``confianca`` é a confiança da emoção predominante;
    ``confianca_deteccao`` é a confiança do detector de faces (YOLOv8) na
    existência da face.
    """

    pontuacoes: dict[str, float]
    predominante: str
    confianca: float
    regiao: RegiaoFace | None = None
    confianca_deteccao: float = 1.0
