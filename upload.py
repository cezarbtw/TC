"""
Router: /api/upload
Recebe o vídeo, dispara a análise e persiste a sessão no banco.
"""

import uuid
import logging
from pathlib import Path
from datetime import date

from fastapi import APIRouter, File, UploadFile, HTTPException

from database import get_connection
from schemas import UploadResponse
from utils.video_processor import analyze_video
from routers.sessions import _fetch_session_detail

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
MAX_FILE_SIZE_MB = 200


@router.post("/upload", response_model=UploadResponse, summary="Envia vídeo para análise")
async def upload_video(file: UploadFile = File(...)):
    """
    Recebe um arquivo de vídeo (MP4, AVI ou MOV), analisa as expressões
    faciais quadro a quadro com DeepFace e salva os resultados no banco.
    """
    # ── Validações básicas ────────────────────────────────────────────────────
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado: {suffix}. Use MP4, AVI ou MOV.",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande ({size_mb:.1f} MB). Limite: {MAX_FILE_SIZE_MB} MB.",
        )

    # ── Salva o arquivo em disco ──────────────────────────────────────────────
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    save_path = UPLOAD_DIR / unique_name
    save_path.write_bytes(content)
    logger.info(f"Arquivo salvo: {save_path}")

    # ── Análise de emoções ────────────────────────────────────────────────────
    try:
        result = analyze_video(str(save_path))
    except Exception as exc:
        save_path.unlink(missing_ok=True)   # limpa arquivo se análise falhar
        logger.exception("Erro na análise do vídeo")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar vídeo: {exc}")

    # ── Persiste no banco ─────────────────────────────────────────────────────
    session_id = _save_session(
        filename=unique_name,
        original_name=file.filename,
        result=result,
    )

    session_detail = _fetch_session_detail(session_id)
    return UploadResponse(
        message="Vídeo analisado com sucesso.",
        session_id=session_id,
        session=session_detail,
    )


def _save_session(filename: str, original_name: str, result: dict) -> int:
    """Insere a sessão e seus dados relacionados no banco. Retorna o ID."""
    with get_connection() as conn:
        # Monta nome sequencial: "Sessão 06"
        count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        session_name = f"Sessão {str(count + 1).zfill(2)}"

        cur = conn.execute(
            """
            INSERT INTO sessions (name, filename, date, duration, frames, predominant, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_name,
                original_name,
                date.today().isoformat(),
                result["duration"],
                result["frames"],
                result["predominant"],
                result["confidence"],
            ),
        )
        session_id = cur.lastrowid

        # Probabilidades médias
        probs_data = [
            (session_id, emo, val)
            for emo, val in result["probabilities"].items()
        ]
        conn.executemany(
            "INSERT INTO emotion_probabilities (session_id, emotion, probability) VALUES (?, ?, ?)",
            probs_data,
        )

        # Timeline (cada ponto no tempo)
        timeline = result.get("timeline", {})
        timeline_data = []
        emotions_in_timeline = list(timeline.keys())
        if emotions_in_timeline:
            n_points = len(timeline[emotions_in_timeline[0]])
            for idx in range(n_points):
                for emo in emotions_in_timeline:
                    val = timeline[emo][idx] if idx < len(timeline[emo]) else 0.0
                    timeline_data.append((session_id, idx, emo, val))

        conn.executemany(
            "INSERT INTO timeline_points (session_id, second_idx, emotion, value) VALUES (?, ?, ?, ?)",
            timeline_data,
        )

    return session_id
