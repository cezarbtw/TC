"""Caso de uso: listar sessões analisadas (GET /sessions)."""
from __future__ import annotations

from app.domain.schemas.session import SessionSchema
from app.domain.services.ports import SessionRepository


class ListSessionsUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    def execute(self) -> list[SessionSchema]:
        return self._repository.list_all()
