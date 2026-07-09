"""Testes do vocabulário de emoções e tradução EN -> PT."""
from __future__ import annotations

from app.domain.entities.emotion import (
    EN_TO_PT,
    PT_EMOTIONS,
    translate_scores_to_pt,
)


def test_all_english_labels_map_to_portuguese():
    assert set(EN_TO_PT.values()) == set(PT_EMOTIONS)
    assert len(EN_TO_PT) == 7


def test_translate_preserves_values_and_order():
    en = {
        "happy": 90.0,
        "sad": 4.0,
        "angry": 2.0,
        "surprise": 1.5,
        "fear": 1.0,
        "disgust": 0.5,
        "neutral": 1.0,
    }
    pt = translate_scores_to_pt(en)
    assert list(pt.keys()) == list(PT_EMOTIONS)
    assert pt["feliz"] == 90.0
    assert pt["triste"] == 4.0
    assert pt["nojo"] == 0.5


def test_translate_fills_missing_emotions_with_zero():
    pt = translate_scores_to_pt({"happy": 100.0})
    assert pt["feliz"] == 100.0
    assert pt["neutro"] == 0.0
    assert set(pt.keys()) == set(PT_EMOTIONS)
