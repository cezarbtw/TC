"""Testes das regras puras de agregação de emoções."""
from __future__ import annotations

from app.domain.entities.emotion import PT_EMOTIONS
from app.domain.services import emotion_aggregation as agg


def _dist(**kwargs: float) -> dict[str, float]:
    base = {emotion: 0.0 for emotion in PT_EMOTIONS}
    base.update(kwargs)
    return base


def test_average_probabilities_computes_mean_per_emotion():
    distributions = [
        _dist(feliz=80.0, triste=20.0),
        _dist(feliz=60.0, triste=40.0),
    ]
    result = agg.average_probabilities(distributions)
    assert result["feliz"] == 70.0
    assert result["triste"] == 30.0
    assert set(result.keys()) == set(PT_EMOTIONS)


def test_average_probabilities_empty_returns_zeros():
    result = agg.average_probabilities([])
    assert all(value == 0.0 for value in result.values())
    assert set(result.keys()) == set(PT_EMOTIONS)


def test_dominant_emotion_picks_highest():
    probs = _dist(feliz=10.0, triste=65.0, neutro=25.0)
    predominant, confidence = agg.dominant_emotion(probs)
    assert predominant == "triste"
    assert confidence == 65.0


def test_build_timeline_transposes_frames():
    distributions = [
        _dist(feliz=70.0),
        _dist(feliz=72.0),
        _dist(feliz=74.0),
    ]
    timeline = agg.build_timeline(distributions)
    assert timeline["feliz"] == [70.0, 72.0, 74.0]
    assert len(timeline["triste"]) == 3
    assert set(timeline.keys()) == set(PT_EMOTIONS)
