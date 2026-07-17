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

    # --- Seleção de dispositivo (aceleração) ---
    # "auto" usa GPU (CUDA) quando disponível, senão CPU. Também aceita "cpu"/"cuda".
    device: str = "auto"

    # --- Amostragem de frames do vídeo ---
    # Taxa de amostragem alvo (frames por segundo analisados). Não processamos
    # todos os frames: ~5 FPS equilibra precisão e custo.
    target_fps: float = 5.0
    # Teto absoluto de frames a analisar, protegendo vídeos longos.
    max_frames_analyzed: int = 600

    # --- Detecção de faces (YOLOv8-face) ---
    # Caminho/nome dos pesos do detector. Baixado uma vez pelo ultralytics.
    face_detector_model: str = "yolov8n-face.pt"
    # Confiança mínima da detecção para considerar a face válida.
    min_detection_confidence: float = 0.5
    # Lado mínimo (px) da face; faces menores são ignoradas (baixa qualidade).
    min_face_size: int = 48

    # --- Classificação emocional (HSEmotion) ---
    # Modelo de 7 classes, compatível com as 7 emoções do frontend.
    emotion_model_name: str = "enet_b2_7"

    # --- Suavização temporal ---
    # Tamanho da janela (nº de frames) da média móvel aplicada à timeline.
    smoothing_window: int = 5


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância única (cacheada) de Settings."""
    return Settings()
