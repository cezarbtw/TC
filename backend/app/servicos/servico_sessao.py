"""Serviço de consulta de sessões (GET /sessions, GET /sessions/{id}).

Também define ``sessao_para_schema``, o mapper explícito entre a entidade de
domínio ``Sessao`` (campos em português) e o contrato de API ``SessaoSchema``
(campos em inglês, para não impactar o frontend) — reusado por
``servico_analise_sessao``.
"""
from __future__ import annotations

from app.dominio.sessao import Sessao
from app.esquemas.sessao import SessaoSchema
from app.nucleo.erros import SessaoNaoEncontradaError
from app.persistencia.repositorio_sessao import RepositorioSessao


def sessao_para_schema(sessao: Sessao) -> SessaoSchema:
    return SessaoSchema(
        id=sessao.id,
        name=sessao.nome,
        source_file=sessao.arquivo_origem,
        date=sessao.data,
        duration=sessao.duracao,
        frames=sessao.frames,
        predominant=sessao.predominante,
        confidence=sessao.confianca,
        probabilities=sessao.probabilidades,
        timeline=sessao.linha_do_tempo,
    )


def listar_sessoes(repositorio: RepositorioSessao) -> list[SessaoSchema]:
    return [sessao_para_schema(sessao) for sessao in repositorio.listar_todas()]


def obter_sessao(repositorio: RepositorioSessao, sessao_id: int) -> SessaoSchema:
    sessao = repositorio.obter(sessao_id)
    if sessao is None:
        raise SessaoNaoEncontradaError(f"Sessão {sessao_id} não encontrada.")
    return sessao_para_schema(sessao)
