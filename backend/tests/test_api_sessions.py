"""Testes de integração dos endpoints de sessão."""
from __future__ import annotations

from app.domain.entities.emotion import PT_EMOTIONS
from app.domain.entities.media import VideoMetadata
from tests.conftest import FakeEmotionAnalyzer, FakeFrameExtractor, make_face


def _video_meta() -> VideoMetadata:
    return VideoMetadata(fps=25.0, total_frames=150, duration_seconds=6.0)


def test_upload_returns_session_matching_frontend_contract(build_client):
    # 3 frames "fictícios"; o analyzer devolve sempre a mesma face feliz.
    extractor = FakeFrameExtractor([object(), object(), object()], _video_meta())
    analyzer = FakeEmotionAnalyzer([make_face("happy", 88.0)])
    client = build_client(analyzer=analyzer, extractor=extractor)

    response = client.post(
        "/sessions/upload",
        files={"file": ("consulta.mp4", b"fake-video", "video/mp4")},
    )

    assert response.status_code == 200
    session = response.json()
    # Campos exatos consumidos pelo frontend (mockData.js).
    assert session["id"] == 1
    assert session["name"] == "Sessão 01"
    assert session["sourceFile"] == "consulta.mp4"  # camelCase via alias
    assert session["duration"] == "00:06"
    assert session["frames"] == 150
    assert session["predominant"] == "feliz"
    assert session["confidence"] == 88.0
    assert set(session["probabilities"].keys()) == set(PT_EMOTIONS)
    assert set(session["timeline"].keys()) == set(PT_EMOTIONS)
    assert len(session["timeline"]["feliz"]) == 3  # 1 ponto por frame com face


def test_upload_without_faces_returns_422(build_client):
    extractor = FakeFrameExtractor([object(), object()], _video_meta())
    analyzer = FakeEmotionAnalyzer([])  # nenhuma face em nenhum frame
    client = build_client(analyzer=analyzer, extractor=extractor)

    response = client.post(
        "/sessions/upload",
        files={"file": ("vazio.mp4", b"fake-video", "video/mp4")},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_and_get_session(build_client):
    extractor = FakeFrameExtractor([object()], _video_meta())
    analyzer = FakeEmotionAnalyzer([make_face("sad", 70.0)])
    client = build_client(analyzer=analyzer, extractor=extractor)

    client.post("/sessions/upload", files={"file": ("a.mp4", b"x", "video/mp4")})

    listed = client.get("/sessions").json()
    assert len(listed) == 1
    assert listed[0]["predominant"] == "triste"

    detail = client.get(f"/sessions/{listed[0]['id']}").json()
    assert detail["id"] == listed[0]["id"]

    missing = client.get("/sessions/999")
    assert missing.status_code == 404
