"""Repositório de sessões em memória.

Implementação simples e thread-safe o suficiente para um protótipo acadêmico,
sem banco de dados. Para produção, bastaria criar outro adapter (ex.: SQLAlchemy)
implementando a mesma porta ``SessionRepository`` — as regras de negócio não
mudam.
"""
from __future__ import annotations

from threading import Lock

from app.domain.entities.session import SessionDraft
from app.domain.schemas.session import SessionSchema
from app.domain.services.ports import SessionRepository


class InMemorySessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._sessions: dict[int, SessionSchema] = {}
        self._counter = 0
        self._lock = Lock()

    def create(self, draft: SessionDraft) -> SessionSchema:
        with self._lock:
            self._counter += 1
            session_id = self._counter
            session = SessionSchema(
                id=session_id,
                name=f"Sessão {session_id:02d}",
                source_file=draft.source_file,
                date=draft.date,
                duration=draft.duration,
                frames=draft.frames,
                predominant=draft.predominant,
                confidence=draft.confidence,
                probabilities=draft.probabilities,
                timeline=draft.timeline,
            )
            self._sessions[session_id] = session
            return session

    def list_all(self) -> list[SessionSchema]:
        with self._lock:
            # Mais recentes primeiro (o frontend usa data[0] como sessão atual).
            return [self._sessions[key] for key in sorted(self._sessions, reverse=True)]

    def get(self, session_id: int) -> SessionSchema | None:
        with self._lock:
            return self._sessions.get(session_id)
