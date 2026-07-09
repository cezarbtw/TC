"""Validação de uploads (tipo e tamanho) reutilizável pelos routers."""
from __future__ import annotations

from fastapi import UploadFile

from app.core.errors import FileTooLargeError, InvalidMediaError, UnsupportedMediaTypeError


async def read_validated_upload(
    file: UploadFile,
    allowed_types: set[str],
    max_bytes: int,
    kind_label: str,
) -> bytes:
    """Lê o arquivo enviado validando content-type e tamanho.

    Retorna os bytes do arquivo ou lança uma exceção de domínio apropriada.
    """
    content_type = (file.content_type or "").lower()
    if content_type not in allowed_types:
        raise UnsupportedMediaTypeError(
            f"Tipo '{file.content_type}' não suportado para {kind_label}. "
            f"Formatos aceitos: {', '.join(sorted(allowed_types))}."
        )

    data = await file.read()
    if not data:
        raise InvalidMediaError(f"O {kind_label} enviado está vazio.")
    if len(data) > max_bytes:
        raise FileTooLargeError(
            f"O {kind_label} excede o limite de {max_bytes // (1024 * 1024)} MB."
        )
    return data
