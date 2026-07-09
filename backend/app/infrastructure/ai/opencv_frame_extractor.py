"""Adapter de extração de frames de vídeo via OpenCV."""
from __future__ import annotations

from typing import Any

from app.core.errors import InvalidMediaError
from app.core.logging import get_logger
from app.domain.entities.media import VideoMetadata
from app.domain.services.ports import FrameExtractor

logger = get_logger(__name__)


class OpenCVFrameExtractor(FrameExtractor):
    """Amostra frames uniformemente ao longo de um vídeo.

    Usa ``grab()`` para pular frames de forma barata (sem decodificar) e
    ``retrieve()`` apenas nos frames amostrados, economizando processamento em
    vídeos longos.
    """

    def extract(
        self, video_path: str, sample_count: int, max_frames: int
    ) -> tuple[list[Any], VideoMetadata]:
        import cv2  # import tardio

        capture = cv2.VideoCapture(video_path)
        if not capture.isOpened():
            raise InvalidMediaError("Não foi possível abrir o vídeo enviado.")

        try:
            fps = float(capture.get(cv2.CAP_PROP_FPS)) or 25.0
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_seconds = total_frames / fps if fps > 0 and total_frames > 0 else 0.0

            target = max(1, min(sample_count, max_frames))
            # Passo de amostragem: distribui os pontos ao longo do vídeo.
            if total_frames > 0:
                step = max(1, total_frames // target)
            else:
                step = max(1, int(fps))  # fallback quando o total é desconhecido

            frames: list[Any] = []
            index = 0
            while len(frames) < target:
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
            "Vídeo processado: %d frames amostrados de %d totais (%.1f fps).",
            len(frames),
            total_frames,
            fps,
        )
        return frames, VideoMetadata(
            fps=fps, total_frames=total_frames, duration_seconds=duration_seconds
        )
