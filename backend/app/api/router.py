"""Agregador de routers da API."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import emotion, sessions

api_router = APIRouter()
api_router.include_router(emotion.router)
api_router.include_router(sessions.router)
