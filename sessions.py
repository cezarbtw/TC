"""
Router: /api/sessions
CRUD de sessões — listar, detalhar e deletar.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from database import get_connection
from schemas import SessionDetail, SessionSummary, EmotionProbabilities

router = APIRouter()

EMOTIONS = ["feliz", "triste", "raiva", "surpresa", "medo", "nojo", "neutro"]


# ─── Listar todas as sessões (resumo) ────────────────────────────────────────

@router.get("/sessions", response_model=List[SessionSummary], summary="Lista todas as sessões")
def list_sessions():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, date, duration, frames, predominant, confidence FROM sessions ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Detalhar uma sessão ──────────────────────────────────────────────────────

@router.get("/sessions/{session_id}", response_model=SessionDetail, summary="Detalha uma sessão")
def get_session(session_id: int):
    detail = _fetch_session_detail(session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return detail


# ─── Deletar uma sessão ───────────────────────────────────────────────────────

@router.delete("/sessions/{session_id}", summary="Remove uma sessão")
def delete_session(session_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sessão não encontrada.")
        # CASCADE deleta probabilidades e timeline automaticamente
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return {"message": f"Sessão {session_id} removida com sucesso."}


# ─── Função interna (usada também pelo router de upload) ─────────────────────

def _fetch_session_detail(session_id: int) -> SessionDetail | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()

        if not row:
            return None

        session = dict(row)

        # Probabilidades
        prob_rows = conn.execute(
            "SELECT emotion, probability FROM emotion_probabilities WHERE session_id = ?",
            (session_id,),
        ).fetchall()
        probs_dict = {r["emotion"]: r["probability"] for r in prob_rows}

        # Garante que todas as emoções estejam presentes (mesmo que zero)
        for emo in EMOTIONS:
            probs_dict.setdefault(emo, 0.0)

        # Timeline
        tl_rows = conn.execute(
            """
            SELECT second_idx, emotion, value
            FROM timeline_points
            WHERE session_id = ?
            ORDER BY second_idx ASC
            """,
            (session_id,),
        ).fetchall()

        timeline: dict[str, list] = {e: [] for e in EMOTIONS}
        if tl_rows:
            max_idx = max(r["second_idx"] for r in tl_rows)
            # Monta listas indexadas por segundo
            tl_map: dict[tuple, float] = {(r["second_idx"], r["emotion"]): r["value"] for r in tl_rows}
            for idx in range(max_idx + 1):
                for emo in EMOTIONS:
                    timeline[emo].append(tl_map.get((idx, emo), 0.0))

    return SessionDetail(
        id=session["id"],
        name=session["name"],
        filename=session["filename"],
        date=session["date"],
        duration=session["duration"],
        frames=session["frames"],
        predominant=session["predominant"],
        confidence=session["confidence"],
        probabilities=EmotionProbabilities(**probs_dict),
        timeline=timeline,
    )
