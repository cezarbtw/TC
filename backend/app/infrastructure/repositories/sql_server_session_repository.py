"""Repositório de sessões persistido em SQL Server (pyodbc puro, sem ORM).

Implementa a mesma porta ``SessionRepository`` usada pelo
``InMemorySessionRepository`` — os casos de uso não sabem qual adapter está
em uso (ver ``app/api/deps/dependencies.py``). Todas as queries são
parametrizadas (``?``) para evitar SQL Injection; nenhuma entrada do usuário
é concatenada diretamente em SQL.
"""
from __future__ import annotations

import json
from datetime import date as date_type
from typing import TYPE_CHECKING, Any

from app.core.config import Settings, get_settings
from app.domain.entities.emotion import PT_EMOTIONS
from app.domain.entities.session import SessionDraft
from app.domain.schemas.session import SessionSchema
from app.domain.services.ports import SessionRepository

if TYPE_CHECKING:
    import pyodbc


class SqlServerSessionRepository(SessionRepository):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def create(self, draft: SessionDraft) -> SessionSchema:
        import pyodbc

        from app.infrastructure.database.connection import connection_scope
        from app.infrastructure.database.exceptions import translate_pyodbc_error

        timeline_json = json.dumps(draft.timeline, ensure_ascii=False)
        session_date = date_type.fromisoformat(draft.date)

        try:
            with connection_scope(self._settings) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO dbo.sessions
                        (name, source_file, session_date, duration, frames,
                         predominant_emotion_id, confidence, timeline_json)
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?, (SELECT id FROM dbo.emotions WHERE code = ?), ?, ?)
                    """,
                    "",
                    draft.source_file,
                    session_date,
                    draft.duration,
                    draft.frames,
                    draft.predominant,
                    draft.confidence,
                    timeline_json,
                )
                session_id = cursor.fetchone()[0]

                name = f"Sessão {session_id:02d}"
                cursor.execute(
                    "UPDATE dbo.sessions SET name = ? WHERE id = ?",
                    name,
                    session_id,
                )

                score_rows = [
                    (session_id, emotion_code, score)
                    for emotion_code, score in draft.probabilities.items()
                ]
                cursor.executemany(
                    """
                    INSERT INTO dbo.session_emotion_scores (session_id, emotion_id, score)
                    VALUES (?, (SELECT id FROM dbo.emotions WHERE code = ?), ?)
                    """,
                    score_rows,
                )
        except pyodbc.Error as exc:
            raise translate_pyodbc_error(exc) from exc

        return SessionSchema(
            id=session_id,
            name=name,
            source_file=draft.source_file,
            date=draft.date,
            duration=draft.duration,
            frames=draft.frames,
            predominant=draft.predominant,
            confidence=draft.confidence,
            probabilities=draft.probabilities,
            timeline=draft.timeline,
        )

    def list_all(self) -> list[SessionSchema]:
        import pyodbc

        from app.infrastructure.database.connection import connection_scope
        from app.infrastructure.database.exceptions import translate_pyodbc_error

        try:
            with connection_scope(self._settings) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT s.id, s.name, s.source_file, s.session_date, s.duration,
                           s.frames, e.code AS predominant, s.confidence, s.timeline_json
                    FROM dbo.sessions AS s
                    JOIN dbo.emotions AS e ON e.id = s.predominant_emotion_id
                    WHERE s.deleted_at IS NULL
                    ORDER BY s.id DESC
                    """
                )
                rows = cursor.fetchall()
                session_ids = [row.id for row in rows]
                scores_by_session = self._fetch_probabilities(cursor, session_ids)
        except pyodbc.Error as exc:
            raise translate_pyodbc_error(exc) from exc

        return [self._row_to_schema(row, scores_by_session[row.id]) for row in rows]

    def get(self, session_id: int) -> SessionSchema | None:
        import pyodbc

        from app.infrastructure.database.connection import connection_scope
        from app.infrastructure.database.exceptions import translate_pyodbc_error

        try:
            with connection_scope(self._settings) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT s.id, s.name, s.source_file, s.session_date, s.duration,
                           s.frames, e.code AS predominant, s.confidence, s.timeline_json
                    FROM dbo.sessions AS s
                    JOIN dbo.emotions AS e ON e.id = s.predominant_emotion_id
                    WHERE s.id = ? AND s.deleted_at IS NULL
                    """,
                    session_id,
                )
                row = cursor.fetchone()
                if row is None:
                    return None

                probabilities = self._fetch_probabilities(cursor, [session_id])[session_id]
        except pyodbc.Error as exc:
            raise translate_pyodbc_error(exc) from exc

        return self._row_to_schema(row, probabilities)

    @staticmethod
    def _fetch_probabilities(
        cursor: "pyodbc.Cursor", session_ids: list[int]
    ) -> dict[int, dict[str, float]]:
        """Busca, em uma única query, os scores por emoção de várias sessões
        (evita N+1 queries em ``list_all``). Garante as 7 chaves de
        ``PT_EMOTIONS`` sempre presentes, mesmo que faltem linhas."""
        result: dict[int, dict[str, float]] = {
            session_id: {pt: 0.0 for pt in PT_EMOTIONS} for session_id in session_ids
        }
        if not session_ids:
            return result

        placeholders = ",".join("?" for _ in session_ids)
        cursor.execute(
            f"""
            SELECT sc.session_id, e.code, sc.score
            FROM dbo.session_emotion_scores AS sc
            JOIN dbo.emotions AS e ON e.id = sc.emotion_id
            WHERE sc.session_id IN ({placeholders})
            """,
            *session_ids,
        )
        for session_id, code, score in cursor.fetchall():
            result[session_id][code] = float(score)
        return result

    @staticmethod
    def _row_to_schema(row: Any, probabilities: dict[str, float]) -> SessionSchema:
        session_date = row.session_date
        date_value = (
            session_date.isoformat() if hasattr(session_date, "isoformat") else str(session_date)
        )
        return SessionSchema(
            id=row.id,
            name=row.name,
            source_file=row.source_file,
            date=date_value,
            duration=row.duration,
            frames=row.frames,
            predominant=row.predominant,
            confidence=float(row.confidence),
            probabilities=probabilities,
            timeline=json.loads(row.timeline_json),
        )
