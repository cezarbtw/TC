"""Caso de uso: análise emocional de um vídeo de sessão (POST /sessions/upload).

Fluxo: extrai frames amostrados -> classifica emoções por frame (reutilizando o
mesmo EmotionAnalyzer do /emotion/predict) -> agrega em um objeto Session que o
dashboard já sabe consumir.
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
        sample_count: int,
        max_frames: int,
    ) -> None:
        self._extractor = extractor
        self._analyzer = analyzer
        self._repository = repository
        self._sample_count = sample_count
        self._max_frames = max_frames

    def execute(self, video_path: str, source_file: str) -> SessionSchema:
        frames, meta = self._extractor.extract(
            video_path, self._sample_count, self._max_frames
        )

        # Distribuição (em PT) por frame com face detectada.
        distributions: list[dict[str, float]] = []
        for frame in frames:
            faces = self._analyzer.analyze_faces(frame)
            if not faces:
                continue
            primary = max(faces, key=_face_area)  # face de maior área
            distributions.append(translate_scores_to_pt(primary.scores))

        if not distributions:
            raise NoFaceDetectedError(
                "Nenhuma face foi detectada nos frames analisados do vídeo."
            )

        probabilities = agg.average_probabilities(distributions)
        predominant, confidence = agg.dominant_emotion(probabilities)
        timeline = agg.build_timeline(distributions)

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
            "Sessão %s criada a partir de '%s': predominante=%s (%.1f%%), %d frames com face.",
            session.id,
            source_file,
            predominant,
            confidence,
            len(distributions),
        )
        return session


def _face_area(face: FaceEmotion) -> int:
    return face.region.area if face.region else 0
