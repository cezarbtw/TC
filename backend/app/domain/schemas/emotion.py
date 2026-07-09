"""Schemas de resposta do endpoint de análise emocional de imagem."""
from __future__ import annotations

from pydantic import BaseModel, Field


class FaceRegionSchema(BaseModel):
    x: int
    y: int
    w: int
    h: int


class FaceDetailSchema(BaseModel):
    """Detalhe por face detectada (extensão útil para depuração/TCC)."""

    dominant_emotion: str
    confidence: float
    emotions: dict[str, float]
    region: FaceRegionSchema | None = None


class EmotionPredictionResponse(BaseModel):
    """Resposta de ``POST /emotion/predict``.

    Mantém as chaves de emoção em inglês, como produzido pelo DeepFace.
    """

    success: bool = Field(..., description="Indica se o processamento ocorreu sem erros.")
    faces_detected: int = Field(..., ge=0, description="Quantidade de faces detectadas.")
    dominant_emotion: str | None = Field(
        None, description="Emoção predominante da face de maior área (ou nulo se não houver face)."
    )
    confidence: float = Field(
        0.0, ge=0.0, le=100.0, description="Confiança (%) da emoção predominante."
    )
    emotions: dict[str, float] = Field(
        default_factory=dict, description="Distribuição de emoções (%) da face predominante."
    )
    faces: list[FaceDetailSchema] = Field(
        default_factory=list, description="Detalhamento de todas as faces detectadas."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "faces_detected": 1,
                "dominant_emotion": "happy",
                "confidence": 94.5,
                "emotions": {
                    "happy": 94.5,
                    "neutral": 3.2,
                    "sad": 1.1,
                    "angry": 0.5,
                    "fear": 0.4,
                    "surprise": 0.3,
                    "disgust": 0.0,
                },
                "faces": [],
            }
        }
    }
