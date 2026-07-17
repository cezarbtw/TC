"""Injeção de dependências (composition root).

Constrói e injeta os adapters concretos nos casos de uso. Os imports de
infraestrutura (torch/ultralytics/hsemotion/OpenCV) são tardios, feitos dentro das
factories, para que apenas importar este módulo não carregue os modelos de IA — e
para que os testes possam sobrescrever as dependências com fakes leves.

Singletons (``lru_cache``): o analisador (modelo carregado uma vez) e o
repositório em memória (estado compartilhado entre requisições).
"""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.domain.services.ports import (
    EmotionAnalyzer,
    FrameExtractor,
    ImageDecoder,
    SessionRepository,
)


@lru_cache
def get_image_decoder() -> ImageDecoder:
    from app.infrastructure.ai.opencv_decoder import OpenCVImageDecoder

    return OpenCVImageDecoder()


@lru_cache
def get_emotion_analyzer() -> EmotionAnalyzer:
    from app.infrastructure.ai.hsemotion_analyzer import HSEmotionAnalyzer
    from app.infrastructure.ai.yolo_face_detector import YoloFaceDetector

    settings = get_settings()
    detector = YoloFaceDetector(
        model_path=settings.face_detector_model,
        device=settings.device,
    )
    return HSEmotionAnalyzer(
        detector=detector,
        model_name=settings.emotion_model_name,
        device=settings.device,
        min_confidence=settings.min_detection_confidence,
        min_face_size=settings.min_face_size,
    )


def warmup_models() -> None:
    """Carrega detector + classificador na inicialização (evita custo na 1ª
    requisição). Falhas não impedem o boot — são logadas e o carregamento é
    retentado sob demanda."""
    analyzer = get_emotion_analyzer()
    warmup = getattr(analyzer, "warmup", None)
    if callable(warmup):
        warmup()


@lru_cache
def get_frame_extractor() -> FrameExtractor:
    from app.infrastructure.ai.opencv_frame_extractor import OpenCVFrameExtractor

    return OpenCVFrameExtractor()


@lru_cache
def get_session_repository() -> SessionRepository:
    from app.infrastructure.repositories.in_memory_session_repository import (
        InMemorySessionRepository,
    )

    return InMemorySessionRepository()


# --- Factories de casos de uso (dependem das portas acima) ---

def get_predict_emotion_use_case(
    decoder: ImageDecoder = Depends(get_image_decoder),
    analyzer: EmotionAnalyzer = Depends(get_emotion_analyzer),
):
    from app.application.use_cases.predict_emotion import PredictEmotionUseCase

    return PredictEmotionUseCase(decoder=decoder, analyzer=analyzer)


def get_analyze_session_use_case(
    extractor: FrameExtractor = Depends(get_frame_extractor),
    analyzer: EmotionAnalyzer = Depends(get_emotion_analyzer),
    repository: SessionRepository = Depends(get_session_repository),
    settings: Settings = Depends(get_settings),
):
    from app.application.use_cases.analyze_session_video import AnalyzeSessionVideoUseCase

    return AnalyzeSessionVideoUseCase(
        extractor=extractor,
        analyzer=analyzer,
        repository=repository,
        target_fps=settings.target_fps,
        max_frames=settings.max_frames_analyzed,
        smoothing_window=settings.smoothing_window,
    )


def get_list_sessions_use_case(
    repository: SessionRepository = Depends(get_session_repository),
):
    from app.application.use_cases.list_sessions import ListSessionsUseCase

    return ListSessionsUseCase(repository=repository)


def get_session_use_case(
    repository: SessionRepository = Depends(get_session_repository),
):
    from app.application.use_cases.get_session import GetSessionUseCase

    return GetSessionUseCase(repository=repository)
