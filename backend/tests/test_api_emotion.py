"""Testes de integração do endpoint POST /emotion/predict."""
from __future__ import annotations

from tests.conftest import FakeEmotionAnalyzer, make_face


def test_predict_returns_dominant_emotion(build_client):
    analyzer = FakeEmotionAnalyzer([make_face("happy", 94.5)])
    client = build_client(analyzer=analyzer)

    response = client.post(
        "/emotion/predict",
        files={"file": ("face.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["faces_detected"] == 1
    assert body["dominant_emotion"] == "happy"
    assert body["confidence"] == 94.5
    assert body["emotions"]["happy"] == 94.5
    assert set(body["emotions"]).issuperset({"happy", "neutral", "sad", "angry"})


def test_predict_picks_largest_face_as_representative(build_client):
    small = make_face("sad", 80.0, area=50)
    large = make_face("happy", 91.0, area=500)
    client = build_client(analyzer=FakeEmotionAnalyzer([small, large]))

    body = client.post(
        "/emotion/predict",
        files={"file": ("faces.jpg", b"xyz", "image/jpeg")},
    ).json()

    assert body["faces_detected"] == 2
    assert body["dominant_emotion"] == "happy"  # maior área vence


def test_predict_with_no_faces(build_client):
    client = build_client(analyzer=FakeEmotionAnalyzer([]))

    body = client.post(
        "/emotion/predict",
        files={"file": ("empty.jpg", b"xyz", "image/jpeg")},
    ).json()

    assert body["success"] is True
    assert body["faces_detected"] == 0
    assert body["dominant_emotion"] is None
    assert body["emotions"] == {}


def test_predict_rejects_unsupported_type(build_client):
    client = build_client(analyzer=FakeEmotionAnalyzer([make_face("happy", 90.0)]))

    response = client.post(
        "/emotion/predict",
        files={"file": ("clip.mp4", b"xyz", "video/mp4")},
    )

    assert response.status_code == 415
    assert "detail" in response.json()
