"""Seleção de dispositivo de inferência (GPU quando disponível, senão CPU)."""
from __future__ import annotations

from app.nucleo.logs import obter_logger

logger = obter_logger(__name__)


def resolver_dispositivo(preferencia: str = "auto") -> str:
    """Resolve o dispositivo de inferência para PyTorch.

    - ``"auto"``: usa ``cuda`` se houver GPU disponível, senão ``cpu``.
    - ``"cpu"``/``"cuda"``: respeita a preferência explícita.
    """
    normalizada = (preferencia or "auto").lower()
    if normalizada in {"cpu", "cuda"}:
        return normalizada

    try:
        import torch

        if torch.cuda.is_available():
            logger.info("GPU detectada (CUDA) — usando aceleração por GPU.")
            return "cuda"
    except Exception:  # noqa: BLE001 - torch ausente ou falha na checagem
        logger.info("PyTorch/CUDA indisponível — usando CPU.")

    return "cpu"
