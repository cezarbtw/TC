"""Fixtures de teste.

A arquitetura em portas/adapters permite testar a API inteira SEM DeepFace,
TensorFlow ou OpenCV: sobrescrevemos as portas por fakes leves via
``app.dependency_overrides``.
"""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.deps.dependencies import (
    get_emotion_analyzer,
    get_frame_extractor,
    get_image_decoder,
    get_session_repository,
)
from app.domain.entities.emotion import FaceEmotion, FaceRegion
from app.domain.entities.media import VideoMetadata
from app.domain.services.ports import (
    EmotionAnalyzer,
    FrameExtractor,
    ImageDecoder,
    SessionRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.main import create_app


class FakeImageDecoder(ImageDecoder):
    """Não decodifica de verdade: devolve os próprios bytes como 'imagem'."""

    def decode(self, data: bytes) -> Any:
        return data


class FakeEmotionAnalyzer(EmotionAnalyzer):
    """Retorna faces pré-configuradas, ignorando a imagem."""

    def __init__(self, faces: list[FaceEmotion]) -> None:
        self._faces = faces

    def analyze_faces(self, image: Any) -> list[FaceEmotion]:
        return list(self._faces)


class FakeFrameExtractor(FrameExtractor):
    def __init__(self, frames: list[Any], meta: VideoMetadata) -> None:
        self._frames = frames
        self._meta = meta

    def extract(self, video_path: str, sample_count: int, max_frames: int):
        return list(self._frames), self._meta


def make_face(dominant: str, confidence: float, area: int = 100) -> FaceEmotion:
    scores = {
        "angry": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "happy": 0.0,
        "sad": 0.0,
        "surprise": 0.0,
        "neutral": 0.0,
    }
    scores[dominant] = confidence
    scores["neutral"] = round(100.0 - confidence, 1) if dominant != "neutral" else confidence
    return FaceEmotion(
        scores=scores,
        dominant=dominant,
        confidence=confidence,
        region=FaceRegion(x=0, y=0, w=area, h=1),
    )


@pytest.fixture
def build_client():
    """Fábrica de TestClient com portas sobrescritas por fakes."""

    def _build(
        *,
        analyzer: EmotionAnalyzer | None = None,
        extractor: FrameExtractor | None = None,
        repository: SessionRepository | None = None,
    ) -> TestClient:
        app = create_app()
        # Uma única instância de repositório compartilhada por todas as requisições
        # deste client (senão cada request receberia um repo vazio).
        repo = repository or InMemorySessionRepository()
        app.dependency_overrides[get_image_decoder] = lambda: FakeImageDecoder()
        if analyzer is not None:
            app.dependency_overrides[get_emotion_analyzer] = lambda: analyzer
        if extractor is not None:
            app.dependency_overrides[get_frame_extractor] = lambda: extractor
        app.dependency_overrides[get_session_repository] = lambda: repo
        return TestClient(app)

    return _build
