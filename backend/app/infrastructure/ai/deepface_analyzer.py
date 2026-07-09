"""Adapter de análise emocional via DeepFace.

Implementa a porta ``EmotionAnalyzer``. O import do DeepFace é tardio (dentro do
método) porque é pesado (carrega TensorFlow) — assim, importar este módulo não
paga esse custo, e os testes que fazem override da porta não precisam do DeepFace
instalado.

Na primeira análise, o DeepFace baixa os pesos do modelo de emoção para
``~/.deepface/weights`` (requer internet uma única vez).
"""
from __future__ import annotations

from typing import Any

from app.core.errors import EmotionAnalysisError
from app.core.logging import get_logger
from app.domain.entities.emotion import EN_EMOTIONS, FaceEmotion, FaceRegion

logger = get_logger(__name__)


class DeepFaceEmotionAnalyzer:
    """Detecta faces e classifica emoções usando DeepFace."""

    def __init__(self, detector_backend: str = "opencv", enforce_detection: bool = True) -> None:
        self._detector_backend = detector_backend
        self._enforce_detection = enforce_detection

    def analyze_faces(self, image: Any) -> list[FaceEmotion]:
        try:
            from deepface import DeepFace
        except ImportError as exc:  # pragma: no cover - ambiente sem dependência
            raise EmotionAnalysisError(
                "Dependência 'deepface' não instalada. Rode: pip install -r requirements.txt"
            ) from exc

        try:
            results = DeepFace.analyze(
                img_path=image,
                actions=["emotion"],
                detector_backend=self._detector_backend,
                enforce_detection=self._enforce_detection,
                silent=True,
            )
        except ValueError:
            # DeepFace lança ValueError quando enforce_detection=True e nenhuma
            # face é encontrada. Tratamos como "zero faces", não como erro.
            return []
        except Exception as exc:  # noqa: BLE001 - encapsula qualquer falha do modelo
            logger.exception("Falha na análise DeepFace")
            raise EmotionAnalysisError() from exc

        # A partir do DeepFace 0.0.79, analyze() sempre retorna uma lista.
        if isinstance(results, dict):
            results = [results]

        faces: list[FaceEmotion] = []
        for item in results:
            emotion_scores = item.get("emotion", {}) or {}
            scores = {name: float(emotion_scores.get(name, 0.0)) for name in EN_EMOTIONS}
            dominant = str(item.get("dominant_emotion") or _argmax(scores))
            faces.append(
                FaceEmotion(
                    scores=scores,
                    dominant=dominant,
                    confidence=round(scores.get(dominant, 0.0), 1),
                    region=_parse_region(item.get("region")),
                )
            )
        return faces


def _argmax(scores: dict[str, float]) -> str:
    return max(scores, key=scores.get) if scores else "neutral"


def _parse_region(region: Any) -> FaceRegion | None:
    if not isinstance(region, dict):
        return None
    try:
        return FaceRegion(
            x=int(region.get("x", 0)),
            y=int(region.get("y", 0)),
            w=int(region.get("w", 0)),
            h=int(region.get("h", 0)),
        )
    except (TypeError, ValueError):
        return None
