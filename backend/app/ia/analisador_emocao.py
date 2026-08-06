"""Adapter de análise emocional via HSEmotion (substitui o DeepFace).

Pipeline por imagem:
  1. Detecta faces com YOLOv8-face.
  2. Descarta faces com confiança baixa ou tamanho insuficiente.
  3. Alinha a face pelos olhos e recorta com margem.
  4. Classifica a emoção com HSEmotion (modelo de 7 classes).

É usado pelo pipeline de análise de vídeo (um frame por vez).

Os imports pesados (torch/hsemotion/ultralytics/cv2) são tardios, para não
carregar o backend de IA apenas ao importar o módulo, e o modelo é carregado uma
única vez (ver ``aquecer``/``_garantir_carregado``).
"""
from __future__ import annotations

from typing import Any

from app.dominio.emocao import EMOCOES_EN, EmocaoFace, RegiaoFace
from app.ia.alinhamento_face import alinhar_e_recortar
from app.ia.detector_face import DetectorFaceYolo
from app.ia.dispositivo import resolver_dispositivo
from app.nucleo.erros import ErroAnaliseEmocional
from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)

# Rótulos do HSEmotion -> rótulos canônicos internos (EN). "contempt" (presente
# apenas nos modelos de 8 classes) não existe no frontend e é descartado.
_HSEMOTION_PARA_EN: dict[str, str | None] = {
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
_HSEMOTION_7_ORDEM_EN: tuple[str, ...] = (
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
)


class AnalisadorEmocaoHSEmotion:
    def __init__(
        self,
        detector: DetectorFaceYolo,
        model_name: str,
        device: str,
        min_confidence: float,
        min_face_size: int,
    ) -> None:
        self._detector = detector
        self._model_name = model_name
        self._device = resolver_dispositivo(device)
        self._min_confidence = min_confidence
        self._min_face_size = min_face_size
        self._recognizer: Any | None = None

    def _garantir_carregado(self) -> Any:
        if self._recognizer is None:
            try:
                from hsemotion.facial_emotions import HSEmotionRecognizer
            except ImportError as exc:  # pragma: no cover - ambiente sem dependência
                raise ErroAnaliseEmocional(
                    "Dependência 'hsemotion' não instalada. Rode: "
                    "pip install -r requirements.txt"
                ) from exc

            logger.info(
                "Carregando classificador HSEmotion (%s) em %s.",
                self._model_name,
                self._device,
            )
            # A lib hsemotion chama torch.load(path) sem map_location; o
            # checkpoint publicado foi salvo em CUDA, então falha em máquinas
            # sem GPU compatível. Força o mapeamento para o device resolvido
            # apenas durante este carregamento (sem alterar a lib instalada).
            import functools

            import torch

            torch_load_original = torch.load
            torch.load = functools.partial(torch_load_original, map_location=self._device)
            try:
                self._recognizer = HSEmotionRecognizer(
                    model_name=self._model_name, device=self._device
                )
            finally:
                torch.load = torch_load_original
        return self._recognizer

    def aquecer(self) -> None:
        """Carrega detector e classificador antecipadamente (na inicialização)."""
        self._detector.aquecer()
        self._garantir_carregado()

    def analisar_faces(self, imagem: Any) -> list[EmocaoFace]:
        import cv2

        recognizer = self._garantir_carregado()
        deteccoes = self._detector.detectar(imagem, self._min_confidence)

        faces: list[EmocaoFace] = []
        for deteccao in deteccoes:
            if min(deteccao.largura, deteccao.altura) < self._min_face_size:
                continue

            recorte = alinhar_e_recortar(imagem, deteccao)
            if recorte is None:
                continue

            rgb = cv2.cvtColor(recorte, cv2.COLOR_BGR2RGB)
            try:
                _, logits = recognizer.predict_emotions(rgb, logits=True)
            except Exception:  # noqa: BLE001 - uma face ruim não deve abortar tudo
                logger.warning("Falha ao classificar uma face; ignorando-a.", exc_info=True)
                continue

            pontuacoes = _logits_para_pontuacoes(logits, recognizer)
            predominante = max(pontuacoes, key=pontuacoes.get)
            faces.append(
                EmocaoFace(
                    pontuacoes=pontuacoes,
                    predominante=predominante,
                    confianca=round(pontuacoes[predominante], 1),
                    regiao=RegiaoFace(
                        x=deteccao.x1,
                        y=deteccao.y1,
                        w=deteccao.largura,
                        h=deteccao.altura,
                    ),
                    confianca_deteccao=round(deteccao.confianca, 3),
                )
            )
        return faces


def _logits_para_pontuacoes(logits: Any, recognizer: Any) -> dict[str, float]:
    """Converte logits do HSEmotion em porcentagens (0..100) por rótulo canônico.

    Aplica softmax nos logits, mapeia os rótulos do modelo para as 7 emoções
    internas (descartando 'contempt' quando presente) e renormaliza para somar 100.
    """
    import numpy as np

    valores = np.asarray(logits, dtype=np.float64).ravel()
    exp = np.exp(valores - valores.max())
    probabilidades = exp / exp.sum()

    bruto = {emocao: 0.0 for emocao in EMOCOES_EN}
    idx_to_class = getattr(recognizer, "idx_to_class", None)

    if isinstance(idx_to_class, dict) and idx_to_class:
        for indice, probabilidade in enumerate(probabilidades):
            rotulo = str(idx_to_class.get(indice, "")).lower()
            canonico = _HSEMOTION_PARA_EN.get(rotulo)
            if canonico is not None:
                bruto[canonico] += float(probabilidade)
    else:
        # Fallback: assume a ordem canônica dos modelos de 7 classes.
        for emocao, probabilidade in zip(_HSEMOTION_7_ORDEM_EN, probabilidades):
            bruto[emocao] += float(probabilidade)

    total = sum(bruto.values())
    if total <= 0:
        return {emocao: 0.0 for emocao in EMOCOES_EN}
    return {emocao: round(bruto[emocao] * 100.0 / total, 1) for emocao in EMOCOES_EN}
