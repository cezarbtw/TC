"""
Motor de análise de vídeo.

Fluxo:
  1. Recebe o caminho do vídeo
  2. Extrai frames em intervalos regulares (a cada N segundos)
  3. Roda DeepFace em cada frame para detectar emoções
  4. Agrega os resultados: probabilidades médias + timeline por segundo
  5. Retorna um dict pronto para salvar no banco e devolver ao front end

Dependências: opencv-python, deepface, tf-keras (ou tensorflow)
"""

import cv2
import math
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Emoções reconhecidas — mesma ordem do front end
EMOTIONS = ["feliz", "triste", "raiva", "surpresa", "medo", "nojo", "neutro"]

# Mapa DeepFace → chaves do front end
DEEPFACE_TO_APP = {
    "happy":    "feliz",
    "sad":      "triste",
    "angry":    "raiva",
    "surprise": "surpresa",
    "fear":     "medo",
    "disgust":  "nojo",
    "neutral":  "neutro",
}

# Quantos frames por segundo extrair (1 = 1 frame/s, 2 = 2 frames/s…)
SAMPLE_RATE = 1


def _zero_probs() -> Dict[str, float]:
    return {e: 0.0 for e in EMOTIONS}


def analyze_video(video_path: str) -> Dict[str, Any]:
    """
    Analisa o vídeo e retorna um dicionário com:
        - duration   : "MM:SS"
        - frames     : int  (frames amostrados com sucesso)
        - predominant: str
        - confidence : float (0-100)
        - probabilities: {emoção: média_%}
        - timeline   : {emoção: [% por segundo]}
    """
    # Importa aqui para não travar o startup caso DeepFace não esteja instalado
    try:
        from deepface import DeepFace
    except ImportError as exc:
        raise RuntimeError(
            "DeepFace não encontrado. Execute: pip install deepface tf-keras"
        ) from exc

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")

    fps        = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_secs   = math.ceil(total_frames / fps)
    step         = max(1, int(fps / SAMPLE_RATE))   # pula N frames entre amostras

    # Acumuladores
    timeline_raw: Dict[str, list] = defaultdict(list)   # por segundo amostrado
    all_probs: list[Dict[str, float]] = []
    analyzed = 0
    frame_idx = 0

    logger.info(f"Analisando vídeo: {video_path} | fps={fps:.1f} | frames={total_frames}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            probs = _analyze_frame(frame, DeepFace)
            if probs:
                all_probs.append(probs)
                for emo in EMOTIONS:
                    timeline_raw[emo].append(round(probs[emo], 2))
                analyzed += 1

        frame_idx += 1

    cap.release()

    if not all_probs:
        logger.warning("Nenhum rosto detectado — usando distribuição neutra.")
        neutral_probs = _zero_probs()
        neutral_probs["neutro"] = 100.0
        return _build_result(
            duration_secs=total_secs,
            frames=0,
            probabilities=neutral_probs,
            timeline={e: [100.0 if e == "neutro" else 0.0] for e in EMOTIONS},
        )

    # Médias gerais
    avg_probs = _zero_probs()
    for p in all_probs:
        for emo in EMOTIONS:
            avg_probs[emo] += p[emo]
    for emo in EMOTIONS:
        avg_probs[emo] = round(avg_probs[emo] / len(all_probs), 2)

    # Normaliza para somar 100
    avg_probs = _normalize(avg_probs)

    # Emoção predominante
    predominant = max(avg_probs, key=avg_probs.get)
    confidence  = avg_probs[predominant]

    return _build_result(
        duration_secs=total_secs,
        frames=analyzed,
        probabilities=avg_probs,
        timeline=dict(timeline_raw),
        predominant=predominant,
        confidence=confidence,
    )


def _analyze_frame(frame, DeepFace) -> Dict[str, float] | None:
    """Roda DeepFace num único frame. Retorna None se nenhum rosto for detectado."""
    try:
        results = DeepFace.analyze(
            img_path=frame,
            actions=["emotion"],
            enforce_detection=False,   # não lança exceção se não achar rosto
            silent=True,
        )
        # DeepFace pode retornar lista ou dict dependendo da versão
        result = results[0] if isinstance(results, list) else results
        raw_emotions: Dict[str, float] = result.get("emotion", {})

        # Mapeia nomes inglês → português
        probs = _zero_probs()
        for df_key, app_key in DEEPFACE_TO_APP.items():
            probs[app_key] = raw_emotions.get(df_key, 0.0)

        return _normalize(probs)

    except Exception as exc:
        logger.debug(f"Frame ignorado: {exc}")
        return None


def _normalize(probs: Dict[str, float]) -> Dict[str, float]:
    """Garante que os valores somem 100."""
    total = sum(probs.values())
    if total == 0:
        return _zero_probs()
    factor = 100.0 / total
    return {k: round(v * factor, 2) for k, v in probs.items()}


def _build_result(
    duration_secs: int,
    frames: int,
    probabilities: Dict[str, float],
    timeline: Dict[str, list],
    predominant: str = None,
    confidence: float = None,
) -> Dict[str, Any]:
    mins = duration_secs // 60
    secs = duration_secs % 60
    duration_str = f"{mins:02d}:{secs:02d}"

    if predominant is None:
        predominant = max(probabilities, key=probabilities.get)
    if confidence is None:
        confidence = probabilities[predominant]

    return {
        "duration":     duration_str,
        "frames":       frames,
        "predominant":  predominant,
        "confidence":   confidence,
        "probabilities": probabilities,
        "timeline":     timeline,
    }


# ─── Utilitário: extrai duração sem analisar emoções ─────────────────────────

def get_video_duration(video_path: str) -> str:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    secs = math.ceil(frames / fps)
    return f"{secs // 60:02d}:{secs % 60:02d}"
