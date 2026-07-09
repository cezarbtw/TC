"""Caso de uso: obter uma sessão por id (GET /sessions/{id})."""
from __future__ import annotations

from app.core.errors import SessionNotFoundError
from app.domain.schemas.session import SessionSchema
from app.domain.services.ports import SessionRepository


class GetSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: int) -> SessionSchema:
        session = self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Sessão {session_id} não encontrada.")
        return session
