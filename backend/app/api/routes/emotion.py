"""Router de análise emocional de imagem (POST /emotion/predict).

Router "fino": apenas valida o upload e delega ao caso de uso. Nenhuma regra de
negócio aqui.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps.dependencies import get_predict_emotion_use_case
from app.api.deps.validators import read_validated_upload
from app.core.config import Settings, get_settings
from app.domain.schemas.emotion import EmotionPredictionResponse

router = APIRouter(prefix="/emotion", tags=["emotion"])


@router.post(
    "/predict",
    response_model=EmotionPredictionResponse,
    summary="Detecta faces e classifica emoções em uma imagem",
)
async def predict_emotion(
    file: UploadFile = File(..., description="Imagem (JPEG/PNG/WebP/BMP) com uma ou mais faces."),
    use_case=Depends(get_predict_emotion_use_case),
    settings: Settings = Depends(get_settings),
) -> EmotionPredictionResponse:
    image_bytes = await read_validated_upload(
        file,
        allowed_types=settings.allowed_image_types,
        max_bytes=settings.max_upload_bytes,
        kind_label="imagem",
    )
    return use_case.execute(image_bytes)
