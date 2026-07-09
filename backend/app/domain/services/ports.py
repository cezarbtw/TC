"""Portas (interfaces) do domínio.

Definem os contratos que a camada de aplicação usa e que a infraestrutura
implementa (inversão de dependência). Assim, DeepFace/OpenCV/persistência podem
ser trocados ou mockados sem alterar as regras de negócio.

Os frames de imagem são tratados como ``Any`` (numpy.ndarray em tempo de
execução) para não acoplar o domínio ao numpy.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.emotion import FaceEmotion
from app.domain.entities.media import VideoMetadata
from app.domain.entities.session import SessionDraft
from app.domain.schemas.session import SessionSchema


class ImageDecoder(ABC):
    """Decodifica bytes de imagem em uma matriz de pixels (BGR)."""

    @abstractmethod
    def decode(self, data: bytes) -> Any:
        """Retorna a imagem decodificada. Lança InvalidMediaError se inválida."""
        raise NotImplementedError


class EmotionAnalyzer(ABC):
    """Detecta faces e classifica emoções em uma imagem já decodificada."""

    @abstractmethod
    def analyze_faces(self, image: Any) -> list[FaceEmotion]:
        """Retorna uma FaceEmotion por face detectada (lista vazia se nenhuma)."""
        raise NotImplementedError


class FrameExtractor(ABC):
    """Extrai frames amostrados de um arquivo de vídeo."""

    @abstractmethod
    def extract(
        self, video_path: str, sample_count: int, max_frames: int
    ) -> tuple[list[Any], VideoMetadata]:
        """Retorna (frames amostrados, metadados do vídeo)."""
        raise NotImplementedError


class SessionRepository(ABC):
    """Persistência de sessões analisadas."""

    @abstractmethod
    def create(self, draft: SessionDraft) -> SessionSchema:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[SessionSchema]:
        raise NotImplementedError

    @abstractmethod
    def get(self, session_id: int) -> SessionSchema | None:
        raise NotImplementedError
