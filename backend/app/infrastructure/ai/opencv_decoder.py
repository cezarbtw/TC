"""Adapter de decodificação de imagem via OpenCV."""
from __future__ import annotations

from typing import Any

import numpy as np

from app.core.errors import InvalidMediaError
from app.core.logging import get_logger
from app.domain.services.ports import ImageDecoder

logger = get_logger(__name__)


class OpenCVImageDecoder(ImageDecoder):
    """Decodifica bytes de imagem em uma matriz BGR (numpy.ndarray)."""

    def decode(self, data: bytes) -> Any:
        import cv2  # import tardio: mantém o pacote domínio/testes livre de cv2

        if not data:
            raise InvalidMediaError("Arquivo de imagem vazio.")

        buffer = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            logger.warning("Falha ao decodificar imagem (%d bytes).", len(data))
            raise InvalidMediaError("Não foi possível decodificar a imagem enviada.")
        return image
