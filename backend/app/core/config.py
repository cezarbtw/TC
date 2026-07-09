"""Configurações da aplicação (12-factor: valores vêm de variáveis de ambiente).

Usa pydantic-settings para tipar e validar a configuração. Todas as variáveis
podem ser sobrescritas por ambiente com o prefixo ``EMOTIONLENS_`` ou por um
arquivo ``.env`` na raiz do backend.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parâmetros de execução do backend de análise emocional."""

    model_config = SettingsConfigDict(
        env_prefix="EMOTIONLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Metadados da aplicação ---
    app_name: str = "EmotionLens API"
    app_version: str = "1.0.0"
    debug: bool = False

    # --- CORS (origem do frontend Vite/React) ---
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --- Limites de upload ---
    # 200 MB: mesmo limite validado no frontend (utils/constants.js).
    max_upload_bytes: int = 200 * 1024 * 1024
    allowed_image_types: set[str] = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/bmp",
    }
    allowed_video_types: set[str] = {
        "video/mp4",
        "video/avi",
        "video/x-msvideo",
        "video/quicktime",
    }

    # --- Parâmetros de análise (DeepFace / OpenCV) ---
    # Backend de detecção de faces do DeepFace. "opencv" é leve e não exige
    # download extra de pesos; "retinaface"/"mtcnn" são mais precisos porém
    # mais pesados.
    detector_backend: str = "opencv"
    # Quando True, o DeepFace lança erro se nenhuma face for encontrada — usamos
    # isso para contar faces de forma confiável.
    enforce_detection: bool = True
    # Nº de frames amostrados de um vídeo para compor a linha do tempo.
    frame_sample_count: int = 30
    # Teto de frames a decodificar, evitando processar vídeos longos por inteiro.
    max_frames_analyzed: int = 300


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância única (cacheada) de Settings."""
    return Settings()
