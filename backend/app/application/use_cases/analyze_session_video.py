"""Caso de uso: análise emocional de um vídeo de sessão (POST /sessions/upload).

Pipeline (HSEmotion):
  1. Amostra frames do vídeo a ~target_fps (não processa todos os frames).
  2. Para cada frame, detecta/alinha/classifica via EmotionAnalyzer (o mesmo
     usado por /emotion/predict — sem duplicar lógica).
  3. Ignora frames sem face válida (detector já filtra confiança/tamanho).
  4. Aplica suavização temporal (média móvel) às distribuições por frame.
  5. Agrega em um objeto Session no MESMO formato consumido pelo dashboard.
"""
from __future__ import annotations

from datetime import date

from app.core.errors import NoFaceDetectedError
from app.core.logging import get_logger
from app.domain.entities.emotion import FaceEmotion, translate_scores_to_pt
from app.domain.entities.session import SessionDraft
from app.domain.schemas.session import SessionSchema
from app.domain.services import emotion_aggregation as agg
from app.domain.services.ports import EmotionAnalyzer, FrameExtractor, SessionRepository

logger = get_logger(__name__)


class AnalyzeSessionVideoUseCase:
    def __init__(
        self,
        extractor: FrameExtractor,
        analyzer: EmotionAnalyzer,
        repository: SessionRepository,
        target_fps: float,
        max_frames: int,
        smoothing_window: int,
    ) -> None:
        self._extractor = extractor
        self._analyzer = analyzer
        self._repository = repository
        self._target_fps = target_fps
        self._max_frames = max_frames
        self._smoothing_window = smoothing_window

    def execute(self, video_path: str, source_file: str) -> SessionSchema:
        frames, meta = self._extractor.extract(
            video_path, self._target_fps, self._max_frames
        )

        # Distribuição (em PT) por frame com face válida. O detector (YOLOv8) já
        # descarta faces com baixa confiança ou tamanho insuficiente.
        distributions: list[dict[str, float]] = []
        for frame in frames:
            faces = self._analyzer.analyze_faces(frame)
            if not faces:
                continue
            primary = max(faces, key=_face_score)  # face principal (maior/mais confiável)
            distributions.append(translate_scores_to_pt(primary.scores))

        if not distributions:
            raise NoFaceDetectedError(
                "Nenhuma face foi detectada nos frames analisados do vídeo."
            )

        # Suavização temporal antes de agregar/plotar a timeline.
        smoothed = agg.smooth_distributions(distributions, self._smoothing_window)

        probabilities = agg.average_probabilities(smoothed)
        predominant, _ = agg.dominant_emotion(probabilities)
        confidence = agg.average_confidence(smoothed)
        timeline = agg.build_timeline(smoothed)

        draft = SessionDraft(
            source_file=source_file,
            date=date.today().isoformat(),
            duration=meta.duration_label,
            frames=meta.total_frames or len(distributions),
            predominant=predominant,
            confidence=confidence,
            probabilities=probabilities,
            timeline=timeline,
        )
        session = self._repository.create(draft)
        logger.info(
            "Sessão %s criada a partir de '%s': predominante=%s (%.1f%%), "
            "%d frames com face de %d amostrados.",
            session.id,
            source_file,
            predominant,
            confidence,
            len(distributions),
            len(frames),
        )
        return session


def _face_score(face: FaceEmotion) -> tuple[int, float]:
    """Critério de seleção da face principal: maior área e, em empate, maior
    confiança de detecção."""
    area = face.region.area if face.region else 0
    return area, face.detection_confidence
