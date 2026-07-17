"""Adapter de análise emocional via HSEmotion (substitui o DeepFace).

Pipeline por imagem:
  1. Detecta faces com YOLOv8-face.
  2. Descarta faces com confiança baixa ou tamanho insuficiente.
  3. Alinha a face pelos olhos e recorta com margem.
  4. Classifica a emoção com HSEmotion (modelo de 7 classes).

Implementa a porta ``EmotionAnalyzer``, portanto é usado tanto pelo endpoint de
imagem (``/emotion/predict``) quanto pelo pipeline de vídeo — sem duplicar lógica.

Os imports pesados (torch/hsemotion/ultralytics/cv2) são tardios, para não
carregar o backend de IA apenas ao importar o módulo, e o modelo é carregado uma
única vez (ver ``warmup``/``_ensure_loaded``).
"""
from __future__ import annotations

from typing import Any

from app.core.errors import EmotionAnalysisError
from app.core.logging import get_logger
from app.domain.entities.emotion import EN_EMOTIONS, FaceEmotion, FaceRegion
from app.domain.services.ports import EmotionAnalyzer
from app.infrastructure.ai.device import resolve_device
from app.infrastructure.ai.face_alignment import align_and_crop
from app.infrastructure.ai.yolo_face_detector import YoloFaceDetector

logger = get_logger(__name__)

# Rótulos do HSEmotion -> rótulos canônicos internos (EN). "contempt" (presente
# apenas nos modelos de 8 classes) não existe no frontend e é descartado.
_HSEMOTION_TO_EN: dict[str, str | None] = {
    "anger": "angry",
    "disgust": "disgust",
    "fear": "fear",
    "happiness": "happy",
    "neutral": "neutral",
    "sadness": "sad",
    "surprise": "surprise",
    "contempt": None,
}

# Ordem canônica de fallback dos modelos de 7 classes do HSEmotion.
_HSEMOTION_7_ORDER_EN: tuple[str, ...] = (
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
)


class HSEmotionAnalyzer(EmotionAnalyzer):
    def __init__(
        self,
        detector: YoloFaceDetector,
        model_name: str,
        device: str,
        min_confidence: float,
        min_face_size: int,
    ) -> None:
        self._detector = detector
        self._model_name = model_name
        self._device = resolve_device(device)
        self._min_confidence = min_confidence
        self._min_face_size = min_face_size
        self._recognizer: Any | None = None

    def _ensure_loaded(self) -> Any:
        if self._recognizer is None:
            try:
                from hsemotion.facial_emotions import HSEmotionRecognizer
            except ImportError as exc:  # pragma: no cover - ambiente sem dependência
                raise EmotionAnalysisError(
                    "Dependência 'hsemotion' não instalada. Rode: "
                    "pip install -r requirements.txt"
                ) from exc

            logger.info(
                "Carregando classificador HSEmotion (%s) em %s.",
                self._model_name,
                self._device,
            )
            self._recognizer = HSEmotionRecognizer(
                model_name=self._model_name, device=self._device
            )
        return self._recognizer

    def warmup(self) -> None:
        """Carrega detector e classificador antecipadamente (na inicialização)."""
        self._detector.warmup()
        self._ensure_loaded()

    def analyze_faces(self, image: Any) -> list[FaceEmotion]:
        import cv2

        recognizer = self._ensure_loaded()
        detections = self._detector.detect(image, self._min_confidence)

        faces: list[FaceEmotion] = []
        for detection in detections:
            if min(detection.width, detection.height) < self._min_face_size:
                continue

            crop = align_and_crop(image, detection)
            if crop is None:
                continue

            rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            try:
                _, logits = recognizer.predict_emotions(rgb, logits=True)
            except Exception:  # noqa: BLE001 - uma face ruim não deve abortar tudo
                logger.warning("Falha ao classificar uma face; ignorando-a.", exc_info=True)
                continue

            scores = _logits_to_scores(logits, recognizer)
            dominant = max(scores, key=scores.get)
            faces.append(
                FaceEmotion(
                    scores=scores,
                    dominant=dominant,
                    confidence=round(scores[dominant], 1),
                    region=FaceRegion(
                        x=detection.x1,
                        y=detection.y1,
                        w=detection.width,
                        h=detection.height,
                    ),
                    detection_confidence=round(detection.confidence, 3),
                )
            )
        return faces


def _logits_to_scores(logits: Any, recognizer: Any) -> dict[str, float]:
    """Converte logits do HSEmotion em porcentagens (0..100) por rótulo canônico.

    Aplica softmax nos logits, mapeia os rótulos do modelo para as 7 emoções
    internas (descartando 'contempt' quando presente) e renormaliza para somar 100.
    """
    import numpy as np

    values = np.asarray(logits, dtype=np.float64).ravel()
    exp = np.exp(values - values.max())
    probabilities = exp / exp.sum()

    raw = {emotion: 0.0 for emotion in EN_EMOTIONS}
    idx_to_class = getattr(recognizer, "idx_to_class", None)

    if isinstance(idx_to_class, dict) and idx_to_class:
        for index, probability in enumerate(probabilities):
            label = str(idx_to_class.get(index, "")).lower()
            canonical = _HSEMOTION_TO_EN.get(label)
            if canonical is not None:
                raw[canonical] += float(probability)
    else:
        # Fallback: assume a ordem canônica dos modelos de 7 classes.
        for emotion, probability in zip(_HSEMOTION_7_ORDER_EN, probabilities):
            raw[emotion] += float(probability)

    total = sum(raw.values())
    if total <= 0:
        return {emotion: 0.0 for emotion in EN_EMOTIONS}
    return {emotion: round(raw[emotion] * 100.0 / total, 1) for emotion in EN_EMOTIONS}
