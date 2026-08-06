"""Alinhamento facial antes da classificação de emoções.

Alinha a face rotacionando a imagem de modo que os olhos fiquem na horizontal,
o que reduz a variância de pose e melhora a acurácia do classificador. Quando os
pontos faciais não estão disponíveis, faz apenas o recorte do bounding box.
"""
from __future__ import annotations

from typing import Any

from app.ia.detector_face import FaceDetectada

# Índices dos pontos faciais no padrão de 5 pontos do YOLOv8-face.
_OLHO_ESQUERDO = 0
_OLHO_DIREITO = 1


def alinhar_e_recortar(imagem: Any, face: FaceDetectada, margem: float = 0.2) -> Any:
    """Retorna o recorte facial (BGR) alinhado pelos olhos, com margem.

    ``margem`` expande o bounding box proporcionalmente para incluir contexto
    (testa/queixo), o que ajuda o classificador de emoções.
    """
    import cv2
    import numpy as np

    altura, largura = imagem.shape[:2]

    # Bounding box com margem, respeitando os limites da imagem.
    mx = int(face.largura * margem)
    my = int(face.altura * margem)
    x1 = max(0, face.x1 - mx)
    y1 = max(0, face.y1 - my)
    x2 = min(largura, face.x2 + mx)
    y2 = min(altura, face.y2 + my)
    if x2 <= x1 or y2 <= y1:
        return None

    alinhada = imagem
    if face.pontos_chave and len(face.pontos_chave) > _OLHO_DIREITO:
        olho_esquerdo = face.pontos_chave[_OLHO_ESQUERDO]
        olho_direito = face.pontos_chave[_OLHO_DIREITO]
        dy = olho_direito[1] - olho_esquerdo[1]
        dx = olho_direito[0] - olho_esquerdo[0]
        angulo = float(np.degrees(np.arctan2(dy, dx)))
        # Só compensa rotações relevantes (evita reamostragem desnecessária).
        if abs(angulo) > 1.0:
            centro = (
                float((olho_esquerdo[0] + olho_direito[0]) / 2.0),
                float((olho_esquerdo[1] + olho_direito[1]) / 2.0),
            )
            rotacao = cv2.getRotationMatrix2D(centro, angulo, 1.0)
            alinhada = cv2.warpAffine(
                imagem, rotacao, (largura, altura), flags=cv2.INTER_LINEAR
            )

    recorte = alinhada[y1:y2, x1:x2]
    if recorte.size == 0:
        return None
    return recorte
