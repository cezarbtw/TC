"""Injeção de dependências das rotas.

Constrói e injeta os adapters concretos nos serviços. Os imports de
infraestrutura (torch/ultralytics/hsemotion/OpenCV/pyodbc) são tardios, feitos
dentro das factories, para que apenas importar este módulo não carregue os
modelos de IA — e para que os testes possam sobrescrever as dependências com
fakes leves.

Singletons (``lru_cache``): o analisador (modelo carregado uma vez) e o
repositório de sessões.
"""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, UploadFile

from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.nucleo.erros import ArquivoMuitoGrandeError, MidiaInvalidaError, TipoMidiaNaoSuportadoError


@lru_cache
def obter_analisador_emocao():
    from app.ia.analisador_emocao import AnalisadorEmocaoHSEmotion
    from app.ia.detector_face import DetectorFaceYolo

    configuracoes = obter_configuracoes()
    detector = DetectorFaceYolo(
        model_path=configuracoes.modelo_detector_face,
        device=configuracoes.dispositivo,
    )
    return AnalisadorEmocaoHSEmotion(
        detector=detector,
        model_name=configuracoes.nome_modelo_emocao,
        device=configuracoes.dispositivo,
        min_confidence=configuracoes.confianca_minima_deteccao,
        min_face_size=configuracoes.tamanho_minimo_face,
    )


def aquecer_modelos() -> None:
    """Carrega detector + classificador na inicialização (evita custo na 1ª
    requisição). Falhas não impedem o boot — são logadas e o carregamento é
    retentado sob demanda."""
    analisador = obter_analisador_emocao()
    aquecer = getattr(analisador, "aquecer", None)
    if callable(aquecer):
        aquecer()


@lru_cache
def obter_extrator_frames():
    from app.ia.extrator_frames import ExtratorFramesOpenCV

    return ExtratorFramesOpenCV()


@lru_cache
def obter_repositorio_sessao():
    from app.persistencia.repositorio_sessao import RepositorioSessao

    return RepositorioSessao(obter_configuracoes())


# --- Factories de serviços (dependem das factories acima) ---

def obter_servico_analise_sessao(
    extrator=Depends(obter_extrator_frames),
    analisador=Depends(obter_analisador_emocao),
    repositorio=Depends(obter_repositorio_sessao),
    configuracoes: Configuracoes = Depends(obter_configuracoes),
):
    from app.servicos.servico_analise_sessao import ServicoAnaliseSessao

    return ServicoAnaliseSessao(
        extrator=extrator,
        analisador=analisador,
        repositorio=repositorio,
        fps_alvo=configuracoes.fps_alvo,
        max_frames=configuracoes.max_frames_analisados,
        janela_suavizacao=configuracoes.janela_suavizacao,
    )


async def ler_upload_validado(
    file: UploadFile,
    tipos_permitidos: set[str],
    max_bytes: int,
    rotulo_tipo: str,
) -> bytes:
    """Lê o arquivo enviado validando content-type e tamanho.

    Retorna os bytes do arquivo ou lança uma exceção de domínio apropriada.
    """
    content_type = (file.content_type or "").lower()
    if content_type not in tipos_permitidos:
        raise TipoMidiaNaoSuportadoError(
            f"Tipo '{file.content_type}' não suportado para {rotulo_tipo}. "
            f"Formatos aceitos: {', '.join(sorted(tipos_permitidos))}."
        )

    dados = await file.read()
    if not dados:
        raise MidiaInvalidaError(f"O {rotulo_tipo} enviado está vazio.")
    if len(dados) > max_bytes:
        raise ArquivoMuitoGrandeError(
            f"O {rotulo_tipo} excede o limite de {max_bytes // (1024 * 1024)} MB."
        )
    return dados
