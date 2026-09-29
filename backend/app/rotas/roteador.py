"""Agrega os routers da aplicação em um único roteador."""
from __future__ import annotations

from fastapi import APIRouter

from app.rotas import autenticacao, sessao

roteador_api = APIRouter()
roteador_api.include_router(autenticacao.router)
roteador_api.include_router(sessao.router)
