"""Router de sessões (GET /sessions, GET /sessions/{id}, POST /sessions/upload).

Contrato consumido pelo frontend (frontend/src/services/sessionsService.js).
O router é fino: valida, persiste o vídeo em arquivo temporário (o OpenCV lê por
caminho) e delega ao caso de uso.
"""
from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps.dependencies import (
    get_analyze_session_use_case,
    get_list_sessions_use_case,
    get_session_use_case,
)
from app.api.deps.validators import read_validated_upload
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.domain.schemas.session import SessionSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionSchema], summary="Lista as sessões analisadas")
async def list_sessions(use_case=Depends(get_list_sessions_use_case)) -> list[SessionSchema]:
    return use_case.execute()


@router.get("/{session_id}", response_model=SessionSchema, summary="Obtém uma sessão pelo id")
async def get_session(session_id: int, use_case=Depends(get_session_use_case)) -> SessionSchema:
    return use_case.execute(session_id)


@router.post(
    "/upload",
    response_model=SessionSchema,
    summary="Envia um vídeo de sessão e retorna a análise emocional agregada",
)
async def upload_session(
    file: UploadFile = File(..., description="Vídeo da sessão (MP4/AVI/MOV, até 200 MB)."),
    use_case=Depends(get_analyze_session_use_case),
    settings: Settings = Depends(get_settings),
) -> SessionSchema:
    video_bytes = await read_validated_upload(
        file,
        allowed_types=settings.allowed_video_types,
        max_bytes=settings.max_upload_bytes,
        kind_label="vídeo",
    )

    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        return use_case.execute(tmp_path, source_file=file.filename or "video")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                logger.warning("Não foi possível remover o arquivo temporário %s", tmp_path)
