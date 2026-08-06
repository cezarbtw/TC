"""Adapter de extração de frames de vídeo via OpenCV."""
from __future__ import annotations

from typing import Any

from app.dominio.midia import MetadadosVideo
from app.nucleo.erros import MidiaInvalidaError
from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)


class ExtratorFramesOpenCV:
    """Amostra frames a uma taxa alvo (``target_fps``) ao longo do vídeo.

    Usa ``grab()`` para pular frames de forma barata (sem decodificar) e
    ``retrieve()`` apenas nos frames amostrados, economizando processamento em
    vídeos longos.
    """

    def extrair(
        self, caminho_video: str, fps_alvo: float, max_frames: int
    ) -> tuple[list[Any], MetadadosVideo]:
        import cv2  # import tardio

        captura = cv2.VideoCapture(caminho_video)
        if not captura.isOpened():
            raise MidiaInvalidaError("Não foi possível abrir o vídeo enviado.")

        try:
            fps_origem = float(captura.get(cv2.CAP_PROP_FPS)) or 25.0
            total_frames = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
            duracao_segundos = (
                total_frames / fps_origem if fps_origem > 0 and total_frames > 0 else 0.0
            )

            # Passo de amostragem: 1 frame a cada 'step' para atingir ~fps_alvo.
            fps_efetivo = min(fps_alvo, fps_origem) if fps_alvo > 0 else fps_origem
            step = max(1, int(round(fps_origem / fps_efetivo))) if fps_efetivo > 0 else 1
            limite = max(1, max_frames)

            frames: list[Any] = []
            indice = 0
            while len(frames) < limite:
                capturado = captura.grab()
                if not capturado:
                    break
                if indice % step == 0:
                    ok, frame = captura.retrieve()
                    if ok and frame is not None:
                        frames.append(frame)
                indice += 1
        finally:
            captura.release()

        if not frames:
            raise MidiaInvalidaError("Nenhum frame pôde ser lido do vídeo.")

        logger.info(
            "Vídeo processado: %d frames amostrados (fonte %.1f fps, ~%.1f fps analisados) "
            "de %d frames totais.",
            len(frames),
            fps_origem,
            min(fps_alvo, fps_origem),
            total_frames,
        )
        return frames, MetadadosVideo(
            fps=fps_origem, total_frames=total_frames, duracao_segundos=duracao_segundos
        )
