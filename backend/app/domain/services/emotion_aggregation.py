"""Regras de agregação de emoções ao longo de um vídeo.

Funções puras (sem I/O), testáveis isoladamente. Recebem distribuições por frame
(já em português) e produzem os campos consumidos pelo dashboard.
"""
from __future__ import annotations

from app.domain.entities.emotion import PT_EMOTIONS


def _round1(value: float) -> float:
    return round(float(value), 1)


def average_probabilities(distributions: list[dict[str, float]]) -> dict[str, float]:
    """Média por emoção sobre todos os frames, arredondada a 1 casa.

    Sempre retorna as sete emoções em português, na ordem canônica.
    """
    if not distributions:
        return {emotion: 0.0 for emotion in PT_EMOTIONS}

    totals = {emotion: 0.0 for emotion in PT_EMOTIONS}
    for frame in distributions:
        for emotion in PT_EMOTIONS:
            totals[emotion] += float(frame.get(emotion, 0.0))

    count = len(distributions)
    return {emotion: _round1(totals[emotion] / count) for emotion in PT_EMOTIONS}


def dominant_emotion(probabilities: dict[str, float]) -> tuple[str, float]:
    """Retorna (emoção predominante, confiança). Empate resolve pela ordem PT."""
    predominant = max(PT_EMOTIONS, key=lambda e: probabilities.get(e, 0.0))
    return predominant, _round1(probabilities.get(predominant, 0.0))


def build_timeline(distributions: list[dict[str, float]]) -> dict[str, list[float]]:
    """Transpõe as distribuições por frame em séries por emoção.

    Resultado: ``{ "feliz": [v0, v1, ...], "triste": [...], ... }``.
    """
    return {
        emotion: [_round1(frame.get(emotion, 0.0)) for frame in distributions]
        for emotion in PT_EMOTIONS
    }
