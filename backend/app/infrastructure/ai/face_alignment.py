"""Alinhamento facial antes da classificação de emoções.

Alinha a face rotacionando a imagem de modo que os olhos fiquem na horizontal,
o que reduz a variância de pose e melhora a acurácia do classificador. Quando os
pontos faciais não estão disponíveis, faz apenas o recorte do bounding box.
"""
from __future__ import annotations

from typing import Any

from app.infrastructure.ai.yolo_face_detector import DetectedFace

# Índices dos pontos faciais no padrão de 5 pontos do YOLOv8-face.
_LEFT_EYE = 0
_RIGHT_EYE = 1


def align_and_crop(image: Any, face: DetectedFace, margin: float = 0.2) -> Any:
    """Retorna o recorte facial (BGR) alinhado pelos olhos, com margem.

    ``margin`` expande o bounding box proporcionalmente para incluir contexto
    (testa/queixo), o que ajuda o classificador de emoções.
    """
    import cv2
    import numpy as np

    height, width = image.shape[:2]

    # Bounding box com margem, respeitando os limites da imagem.
    mx = int(face.width * margin)
    my = int(face.height * margin)
    x1 = max(0, face.x1 - mx)
    y1 = max(0, face.y1 - my)
    x2 = min(width, face.x2 + mx)
    y2 = min(height, face.y2 + my)
    if x2 <= x1 or y2 <= y1:
        return None

    aligned = image
    if face.keypoints and len(face.keypoints) > _RIGHT_EYE:
        left_eye = face.keypoints[_LEFT_EYE]
        right_eye = face.keypoints[_RIGHT_EYE]
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = float(np.degrees(np.arctan2(dy, dx)))
        # Só compensa rotações relevantes (evita reamostragem desnecessária).
        if abs(angle) > 1.0:
            center = (
                float((left_eye[0] + right_eye[0]) / 2.0),
                float((left_eye[1] + right_eye[1]) / 2.0),
            )
            rotation = cv2.getRotationMatrix2D(center, angle, 1.0)
            aligned = cv2.warpAffine(
                image, rotation, (width, height), flags=cv2.INTER_LINEAR
            )

    crop = aligned[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    return crop
