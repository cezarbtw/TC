"""Router de sessÃµes (GET /sessions, GET /sessions/{id}, POST /sessions/upload).

Contrato consumido pelo frontend (frontend/src/services/sessionsService.js).
O router Ã© fino: valida, persiste o vÃ­deo em arquivo temporÃ¡rio (o OpenCV lÃª por
caminho) e delega ao serviÃ§o correspondente.
"""
from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile

from app.esquemas.sessao import SessaoSchema
from app.dominio.usuario import Usuario
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.nucleo.logs import obter_logger
from app.rotas.dependencias import (
    ler_upload_validado,
    obter_repositorio_sessao,
    obter_servico_analise_sessao,
    obter_usuario_atual,
)
from app.servicos import servico_sessao

logger = obter_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessaoSchema], summary="Lista as sessÃµes analisadas")
async def listar_sessoes(
    usuario: Usuario = Depends(obter_usuario_atual), repositorio=Depends(obter_repositorio_sessao)
) -> list[SessaoSchema]:
    return servico_sessao.listar_sessoes(repositorio, usuario.id)


@router.get("/{session_id}", response_model=SessaoSchema, summary="ObtÃ©m uma sessÃ£o pelo id")
async def obter_sessao(
    session_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    repositorio=Depends(obter_repositorio_sessao),
) -> SessaoSchema:
    return servico_sessao.obter_sessao(repositorio, session_id, usuario.id)


@router.post(
    "/upload",
    response_model=SessaoSchema,
    summary="Envia um vÃ­deo de sessÃ£o e retorna a anÃ¡lise emocional agregada",
)
async def enviar_sessao(
    file: UploadFile = File(..., description="VÃ­deo da sessÃ£o (MP4/AVI/MOV, atÃ© 200 MB)."),
    servico=Depends(obter_servico_analise_sessao),
    configuracoes: Configuracoes = Depends(obter_configuracoes),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> SessaoSchema:
    bytes_video = await ler_upload_validado(
        file,
        tipos_permitidos=configuracoes.tipos_video_permitidos,
        max_bytes=configuracoes.tamanho_maximo_upload_bytes,
        rotulo_tipo="vÃ­deo",
    )

    sufixo = os.path.splitext(file.filename or "")[1] or ".mp4"
    caminho_tmp: str | None = None
    import time
    from rich.console import Console
    console = Console()
    
    inicio_proc = time.perf_counter()
    console.print(f"\n[bold yellow][START][/bold yellow] Iniciando processamento do vÃ­deo: {file.filename} ...")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
            tmp.write(bytes_video)
            caminho_tmp = tmp.name
        resultado = servico.executar(caminho_tmp, arquivo_origem=file.filename or "video", usuario_id=usuario.id)
        
        fim_proc = time.perf_counter()
        tempo = round(fim_proc - inicio_proc, 2)
        console.print(f"[bold green][SUCESSO][/bold green] Processamento e Criptografia concluídos em [bold cyan]{tempo}s[/bold cyan]!")
        return resultado
    finally:
        if caminho_tmp and os.path.exists(caminho_tmp):
            try:
                os.remove(caminho_tmp)
            except OSError:
                logger.warning("NÃ£o foi possÃ­vel remover o arquivo temporÃ¡rio %s", caminho_tmp)

