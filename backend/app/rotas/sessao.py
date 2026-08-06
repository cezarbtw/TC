"""Router de sessões (GET /sessions, GET /sessions/{id}, POST /sessions/upload).

Contrato consumido pelo frontend (frontend/src/services/sessionsService.js).
O router é fino: valida, persiste o vídeo em arquivo temporário (o OpenCV lê por
caminho) e delega ao serviço correspondente.
"""
from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile

from app.esquemas.sessao import SessaoSchema
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.nucleo.logs import obter_logger
from app.rotas.dependencias import (
    ler_upload_validado,
    obter_repositorio_sessao,
    obter_servico_analise_sessao,
)
from app.servicos import servico_sessao

logger = obter_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessaoSchema], summary="Lista as sessões analisadas")
async def listar_sessoes(repositorio=Depends(obter_repositorio_sessao)) -> list[SessaoSchema]:
    return servico_sessao.listar_sessoes(repositorio)


@router.get("/{session_id}", response_model=SessaoSchema, summary="Obtém uma sessão pelo id")
async def obter_sessao(
    session_id: int, repositorio=Depends(obter_repositorio_sessao)
) -> SessaoSchema:
    return servico_sessao.obter_sessao(repositorio, session_id)


@router.post(
    "/upload",
    response_model=SessaoSchema,
    summary="Envia um vídeo de sessão e retorna a análise emocional agregada",
)
async def enviar_sessao(
    file: UploadFile = File(..., description="Vídeo da sessão (MP4/AVI/MOV, até 200 MB)."),
    servico=Depends(obter_servico_analise_sessao),
    configuracoes: Configuracoes = Depends(obter_configuracoes),
) -> SessaoSchema:
    bytes_video = await ler_upload_validado(
        file,
        tipos_permitidos=configuracoes.tipos_video_permitidos,
        max_bytes=configuracoes.tamanho_maximo_upload_bytes,
        rotulo_tipo="vídeo",
    )

    sufixo = os.path.splitext(file.filename or "")[1] or ".mp4"
    caminho_tmp: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
            tmp.write(bytes_video)
            caminho_tmp = tmp.name
        return servico.executar(caminho_tmp, arquivo_origem=file.filename or "video")
    finally:
        if caminho_tmp and os.path.exists(caminho_tmp):
            try:
                os.remove(caminho_tmp)
            except OSError:
                logger.warning("Não foi possível remover o arquivo temporário %s", caminho_tmp)
