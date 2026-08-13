"""Configurações da aplicação (12-factor: valores vêm de variáveis de ambiente).

Usa pydantic-settings para tipar e validar a configuração. Todas as variáveis
podem ser sobrescritas por ambiente com o prefixo ``EMOTIONLENS_`` ou por um
arquivo ``.env`` na raiz do backend.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    """Parâmetros de execução do backend de análise emocional."""

    model_config = SettingsConfigDict(
        env_prefix="EMOTIONLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Metadados da aplicação ---
    nome_app: str = "EmotionLens API"
    versao_app: str = "1.0.0"
    depuracao: bool = False

    # --- CORS (origem do frontend Vite/React) ---
    origens_cors: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --- Limites de upload ---
    # 200 MB: mesmo limite validado no frontend (utils/constants.js).
    tamanho_maximo_upload_bytes: int = 200 * 1024 * 1024
    tipos_video_permitidos: set[str] = {
        "video/mp4",
        "video/avi",
        "video/x-msvideo",
        "video/quicktime",
    }

    # --- Seleção de dispositivo (aceleração) ---
    # "auto" usa GPU (CUDA) quando disponível, senão CPU. Também aceita "cpu"/"cuda".
    dispositivo: str = "auto"

    # --- Amostragem de frames do vídeo ---
    # Taxa de amostragem alvo (frames por segundo analisados). Não processamos
    # todos os frames: ~5 FPS equilibra precisão e custo.
    fps_alvo: float = 5.0
    # Teto absoluto de frames a analisar, protegendo vídeos longos.
    max_frames_analisados: int = 600

    # --- Detecção de faces (YOLOv8-face) ---
    # Caminho/nome dos pesos do detector. Baixado uma vez pelo ultralytics.
    modelo_detector_face: str = "yolov8n-face.pt"
    # Confiança mínima da detecção para considerar a face válida.
    confianca_minima_deteccao: float = 0.5
    # Lado mínimo (px) da face; faces menores são ignoradas (baixa qualidade).
    tamanho_minimo_face: int = 48

    # --- Classificação emocional (HSEmotion) ---
    # Modelo de 7 classes, compatível com as 7 emoções do frontend.
    nome_modelo_emocao: str = "enet_b2_7"

    # --- Suavização temporal ---
    # Tamanho da janela (nº de frames) da média móvel aplicada à timeline.
    janela_suavizacao: int = 5

    # --- SQL Server ---
    db_servidor: str = "localhost"
    db_banco: str = "EmotionLensDB"
    # Windows Authentication (Trusted_Connection) por padrão — dispensa usuário/senha.
    # Defina como false para usar SQL Authentication (db_usuario/db_senha).
    db_conexao_confiavel: bool = True
    db_usuario: str = ""
    db_senha: str = ""
    db_driver: str = "ODBC Driver 17 for SQL Server"
    db_tempo_limite_conexao: int = 5

    # --- Criptografia em duas camadas (MCE + AES-256-GCM) ---
    chave_criptografia: str = "EmotionLens-AES-Analise-Local-2026"
    chave_mce: str = "EmotionLens-MCE-Mapa-Emocional-2026"


@lru_cache
def obter_configuracoes() -> Configuracoes:
    """Retorna uma instância única (cacheada) de Configuracoes."""
    return Configuracoes()
