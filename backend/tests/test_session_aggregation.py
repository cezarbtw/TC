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


def test_smooth_distributions_preserves_length_and_reduces_noise():
    distributions = [_dist(feliz=0.0), _dist(feliz=100.0), _dist(feliz=0.0)]
    smoothed = agg.smooth_distributions(distributions, window=3)
    assert len(smoothed) == 3
    # O pico isolado é atenuado pela média móvel centrada.
    assert smoothed[1]["feliz"] < 100.0
    assert smoothed[1]["feliz"] > 0.0


def test_smooth_distributions_window_one_is_noop():
    distributions = [_dist(feliz=10.0), _dist(feliz=90.0)]
    smoothed = agg.smooth_distributions(distributions, window=1)
    assert smoothed[0]["feliz"] == 10.0
    assert smoothed[1]["feliz"] == 90.0


def test_average_confidence_uses_per_frame_peak():
    distributions = [
        _dist(feliz=80.0, neutro=20.0),
        _dist(triste=60.0, neutro=40.0),
    ]
    # picos: 80 e 60 -> média 70
    assert agg.average_confidence(distributions) == 70.0
