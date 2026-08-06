"""Detector de faces baseado em YOLOv8-face (ultralytics).

Encapsula o carregamento do modelo (uma única vez) e a inferência, devolvendo
faces com bounding box, confiança e, quando disponíveis, os 5 pontos faciais
usados para alinhamento.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ia.dispositivo import resolver_dispositivo
from app.nucleo.erros import ErroAnaliseEmocional
from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)


@dataclass(frozen=True)
class FaceDetectada:
    """Face detectada em coordenadas de pixel (x1, y1, x2, y2)."""

    x1: int
    y1: int
    x2: int
    y2: int
    confianca: float
    # 5 pontos (olho esq., olho dir., nariz, boca esq., boca dir.) ou None.
    pontos_chave: list[tuple[float, float]] | None = None

    @property
    def largura(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def altura(self) -> int:
        return max(0, self.y2 - self.y1)


class DetectorFaceYolo:
    """Adapter fino sobre o modelo YOLOv8-face."""

    def __init__(self, model_path: str, device: str = "auto") -> None:
        self._model_path = model_path
        self._device = resolver_dispositivo(device)
        self._model: Any | None = None

    def _garantir_carregado(self) -> Any:
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:  # pragma: no cover - ambiente sem dependência
                raise ErroAnaliseEmocional(
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

    def aquecer(self) -> None:
        """Força o carregamento antecipado do modelo (na inicialização)."""
        self._garantir_carregado()

    def detectar(self, imagem: Any, confianca_minima: float) -> list[FaceDetectada]:
        """Detecta faces com confiança >= ``confianca_minima``."""
        model = self._garantir_carregado()
        try:
            resultados = model.predict(
                imagem,
                conf=confianca_minima,
                device=self._device,
                verbose=False,
            )
        except Exception as exc:  # noqa: BLE001 - encapsula falhas do modelo
            logger.exception("Falha na detecção de faces (YOLOv8)")
            raise ErroAnaliseEmocional("Falha na detecção de faces.") from exc

        if not resultados:
            return []

        resultado = resultados[0]
        faces: list[FaceDetectada] = []
        boxes = getattr(resultado, "boxes", None)
        if boxes is None:
            return []

        pontos_chave_xy = _extrair_pontos_chave(resultado)
        for idx in range(len(boxes)):
            x1, y1, x2, y2 = (float(v) for v in boxes.xyxy[idx].tolist())
            confianca = float(boxes.conf[idx].item())
            faces.append(
                FaceDetectada(
                    x1=int(x1),
                    y1=int(y1),
                    x2=int(x2),
                    y2=int(y2),
                    confianca=confianca,
                    pontos_chave=pontos_chave_xy[idx] if pontos_chave_xy else None,
                )
            )
        return faces


def _extrair_pontos_chave(resultado: Any) -> list[list[tuple[float, float]]] | None:
    """Extrai os pontos faciais do resultado do YOLO, se o modelo os fornecer."""
    keypoints = getattr(resultado, "keypoints", None)
    if keypoints is None or getattr(keypoints, "xy", None) is None:
        return None
    try:
        return [
            [(float(x), float(y)) for x, y in face_kps]
            for face_kps in keypoints.xy.tolist()
        ]
    except (TypeError, ValueError):
        return None
