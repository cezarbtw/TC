"""Adapter de extração de frames de vídeo via OpenCV."""
from __future__ import annotations

from typing import Any

from app.core.errors import InvalidMediaError
from app.core.logging import get_logger
from app.domain.entities.media import VideoMetadata
from app.domain.services.ports import FrameExtractor

logger = get_logger(__name__)


class OpenCVFrameExtractor(FrameExtractor):
    """Amostra frames a uma taxa alvo (``target_fps``) ao longo do vídeo.

    Usa ``grab()`` para pular frames de forma barata (sem decodificar) e
    ``retrieve()`` apenas nos frames amostrados, economizando processamento em
    vídeos longos.
    """

    def extract(
        self, video_path: str, target_fps: float, max_frames: int
    ) -> tuple[list[Any], VideoMetadata]:
        import cv2  # import tardio

        capture = cv2.VideoCapture(video_path)
        if not capture.isOpened():
            raise InvalidMediaError("Não foi possível abrir o vídeo enviado.")

        try:
            source_fps = float(capture.get(cv2.CAP_PROP_FPS)) or 25.0
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_seconds = (
                total_frames / source_fps if source_fps > 0 and total_frames > 0 else 0.0
            )

            # Passo de amostragem: 1 frame a cada 'step' para atingir ~target_fps.
            effective_fps = min(target_fps, source_fps) if target_fps > 0 else source_fps
            step = max(1, int(round(source_fps / effective_fps))) if effective_fps > 0 else 1
            limit = max(1, max_frames)

            frames: list[Any] = []
            index = 0
            while len(frames) < limit:
                grabbed = capture.grab()
                if not grabbed:
                    break
                if index % step == 0:
                    ok, frame = capture.retrieve()
                    if ok and frame is not None:
                        frames.append(frame)
                index += 1
        finally:
            capture.release()

        if not frames:
            raise InvalidMediaError("Nenhum frame pôde ser lido do vídeo.")

        logger.info(
            "Vídeo processado: %d frames amostrados (fonte %.1f fps, ~%.1f fps analisados) "
            "de %d frames totais.",
            len(frames),
            source_fps,
            min(target_fps, source_fps),
            total_frames,
        )
        return frames, VideoMetadata(
            fps=source_fps, total_frames=total_frames, duration_seconds=duration_seconds
        )
