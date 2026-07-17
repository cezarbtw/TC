"""Seleção de dispositivo de inferência (GPU quando disponível, senão CPU)."""
from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)


def resolve_device(preference: str = "auto") -> str:
    """Resolve o dispositivo de inferência para PyTorch.

    - ``"auto"``: usa ``cuda`` se houver GPU disponível, senão ``cpu``.
    - ``"cpu"``/``"cuda"``: respeita a preferência explícita.
    """
    normalized = (preference or "auto").lower()
    if normalized in {"cpu", "cuda"}:
        return normalized

    try:
        import torch

        if torch.cuda.is_available():
            logger.info("GPU detectada (CUDA) — usando aceleração por GPU.")
            return "cuda"
    except Exception:  # noqa: BLE001 - torch ausente ou falha na checagem
        logger.info("PyTorch/CUDA indisponível — usando CPU.")

    return "cpu"
