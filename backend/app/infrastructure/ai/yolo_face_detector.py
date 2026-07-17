"""Detector de faces baseado em YOLOv8-face (ultralytics).

Encapsula o carregamento do modelo (uma única vez) e a inferência, devolvendo
faces com bounding box, confiança e, quando disponíveis, os 5 pontos faciais
usados para alinhamento.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.errors import EmotionAnalysisError
from app.core.logging import get_logger
from app.infrastructure.ai.device import resolve_device

logger = get_logger(__name__)


@dataclass(frozen=True)
class DetectedFace:
    """Face detectada em coordenadas de pixel (x1, y1, x2, y2)."""

    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    # 5 pontos (olho esq., olho dir., nariz, boca esq., boca dir.) ou None.
    keypoints: list[tuple[float, float]] | None = None

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)


class YoloFaceDetector:
    """Adapter fino sobre o modelo YOLOv8-face."""

    def __init__(self, model_path: str, device: str = "auto") -> None:
        self._model_path = model_path
        self._device = resolve_device(device)
        self._model: Any | None = None

    def _ensure_loaded(self) -> Any:
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:  # pragma: no cover - ambiente sem dependência
                raise EmotionAnalysisError(
                    "Dependência 'ultralytics' não instalada. Rode: "
                    "pip install -r requirements.txt"
                ) from exc

            logger.info(
                "Carregando detector de faces YOLOv8 (%s) em %s.",
                self._model_path,
                self._device,
            )
            self._model = YOLO(self._model_path)
        return self._model

    def warmup(self) -> None:
        """Força o carregamento antecipado do modelo (na inicialização)."""
        self._ensure_loaded()

    def detect(self, image: Any, min_confidence: float) -> list[DetectedFace]:
        """Detecta faces com confiança >= ``min_confidence``."""
        model = self._ensure_loaded()
        try:
            results = model.predict(
                image,
                conf=min_confidence,
                device=self._device,
                verbose=False,
            )
        except Exception as exc:  # noqa: BLE001 - encapsula falhas do modelo
            logger.exception("Falha na detecção de faces (YOLOv8)")
            raise EmotionAnalysisError("Falha na detecção de faces.") from exc

        if not results:
            return []

        result = results[0]
        faces: list[DetectedFace] = []
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return []

        keypoints_xy = _extract_keypoints(result)
        for idx in range(len(boxes)):
            x1, y1, x2, y2 = (float(v) for v in boxes.xyxy[idx].tolist())
            confidence = float(boxes.conf[idx].item())
            faces.append(
                DetectedFace(
                    x1=int(x1),
                    y1=int(y1),
                    x2=int(x2),
                    y2=int(y2),
                    confidence=confidence,
                    keypoints=keypoints_xy[idx] if keypoints_xy else None,
                )
            )
        return faces


def _extract_keypoints(result: Any) -> list[list[tuple[float, float]]] | None:
    """Extrai os pontos faciais do resultado do YOLO, se o modelo os fornecer."""
    keypoints = getattr(result, "keypoints", None)
    if keypoints is None or getattr(keypoints, "xy", None) is None:
        return None
    try:
        return [
            [(float(x), float(y)) for x, y in face_kps]
            for face_kps in keypoints.xy.tolist()
        ]
    except (TypeError, ValueError):
        return None
