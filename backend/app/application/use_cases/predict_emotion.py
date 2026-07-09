"""Caso de uso: análise emocional de uma imagem única (POST /emotion/predict)."""
from __future__ import annotations

from app.core.logging import get_logger
from app.domain.entities.emotion import FaceEmotion
from app.domain.schemas.emotion import (
    EmotionPredictionResponse,
    FaceDetailSchema,
    FaceRegionSchema,
)
from app.domain.services.ports import EmotionAnalyzer, ImageDecoder

logger = get_logger(__name__)


class PredictEmotionUseCase:
    """Decodifica a imagem, detecta faces e monta a resposta de predição."""

    def __init__(self, decoder: ImageDecoder, analyzer: EmotionAnalyzer) -> None:
        self._decoder = decoder
        self._analyzer = analyzer

    def execute(self, image_bytes: bytes) -> EmotionPredictionResponse:
        image = self._decoder.decode(image_bytes)
        faces = self._analyzer.analyze_faces(image)
        logger.info("Predição de imagem concluída: %d face(s).", len(faces))

        if not faces:
            return EmotionPredictionResponse(
                success=True,
                faces_detected=0,
                dominant_emotion=None,
                confidence=0.0,
                emotions={},
                faces=[],
            )

        # Face representativa = maior área (paciente em primeiro plano).
        primary = max(faces, key=_face_area)
        return EmotionPredictionResponse(
            success=True,
            faces_detected=len(faces),
            dominant_emotion=primary.dominant,
            confidence=round(primary.confidence, 1),
            emotions={k: round(v, 1) for k, v in primary.scores.items()},
            faces=[_to_detail(face) for face in faces],
        )


def _face_area(face: FaceEmotion) -> int:
    return face.region.area if face.region else 0


def _to_detail(face: FaceEmotion) -> FaceDetailSchema:
    region = (
        FaceRegionSchema(x=face.region.x, y=face.region.y, w=face.region.w, h=face.region.h)
        if face.region
        else None
    )
    return FaceDetailSchema(
        dominant_emotion=face.dominant,
        confidence=round(face.confidence, 1),
        emotions={k: round(v, 1) for k, v in face.scores.items()},
        region=region,
    )
