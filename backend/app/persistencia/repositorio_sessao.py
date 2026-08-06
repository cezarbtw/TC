"""Repositório de sessões persistido em SQL Server (pyodbc puro, sem ORM).

Todas as queries são parametrizadas (``?``) para evitar SQL Injection;
nenhuma entrada do usuário é concatenada diretamente em SQL.
"""
from __future__ import annotations

import json
from datetime import date as date_type
from typing import TYPE_CHECKING, Any

from app.dominio.emocao import EMOCOES_PT
from app.dominio.sessao import RascunhoSessao, Sessao
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes

if TYPE_CHECKING:
    import pyodbc


class RepositorioSessao:
    def __init__(self, configuracoes: Configuracoes | None = None) -> None:
        self._configuracoes = configuracoes or obter_configuracoes()

    def criar(self, rascunho: RascunhoSessao) -> Sessao:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        linha_do_tempo_json = json.dumps(rascunho.linha_do_tempo, ensure_ascii=False)
        data_sessao = date_type.fromisoformat(rascunho.data)

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO dbo.sessoes
                        (nome, arquivo_origem, data_sessao, duracao, frames,
                         emocao_predominante_id, confianca, linha_do_tempo_json)
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?, (SELECT id FROM dbo.emocoes WHERE codigo = ?), ?, ?)
                    """,
                    "",
                    rascunho.arquivo_origem,
                    data_sessao,
                    rascunho.duracao,
                    rascunho.frames,
                    rascunho.predominante,
                    rascunho.confianca,
                    linha_do_tempo_json,
                )
                sessao_id = cursor.fetchone()[0]

                nome = f"Sessão {sessao_id:02d}"
                cursor.execute(
                    "UPDATE dbo.sessoes SET nome = ? WHERE id = ?",
                    nome,
                    sessao_id,
                )

                linhas_pontuacao = [
                    (sessao_id, codigo_emocao, pontuacao)
                    for codigo_emocao, pontuacao in rascunho.probabilidades.items()
                ]
                cursor.executemany(
                    """
                    INSERT INTO dbo.pontuacoes_emocao_sessao (sessao_id, emocao_id, pontuacao)
                    VALUES (?, (SELECT id FROM dbo.emocoes WHERE codigo = ?), ?)
                    """,
                    linhas_pontuacao,
                )
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        return Sessao(
            id=sessao_id,
            nome=nome,
            arquivo_origem=rascunho.arquivo_origem,
            data=rascunho.data,
            duracao=rascunho.duracao,
            frames=rascunho.frames,
            predominante=rascunho.predominante,
            confianca=rascunho.confianca,
            probabilidades=rascunho.probabilidades,
            linha_do_tempo=rascunho.linha_do_tempo,
        )

    def listar_todas(self) -> list[Sessao]:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT s.id, s.nome, s.arquivo_origem, s.data_sessao, s.duracao,
                           s.frames, e.codigo AS predominante, s.confianca, s.linha_do_tempo_json
                    FROM dbo.sessoes AS s
                    JOIN dbo.emocoes AS e ON e.id = s.emocao_predominante_id
                    WHERE s.excluido_em IS NULL
                    ORDER BY s.id DESC
                    """
                )
                linhas = cursor.fetchall()
                sessao_ids = [linha.id for linha in linhas]
                pontuacoes_por_sessao = self._buscar_probabilidades(cursor, sessao_ids)
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        return [
            self._linha_para_entidade(linha, pontuacoes_por_sessao[linha.id])
            for linha in linhas
        ]

    def obter(self, sessao_id: int) -> Sessao | None:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT s.id, s.nome, s.arquivo_origem, s.data_sessao, s.duracao,
                           s.frames, e.codigo AS predominante, s.confianca, s.linha_do_tempo_json
                    FROM dbo.sessoes AS s
                    JOIN dbo.emocoes AS e ON e.id = s.emocao_predominante_id
                    WHERE s.id = ? AND s.excluido_em IS NULL
                    """,
                    sessao_id,
                )
                linha = cursor.fetchone()
                if linha is None:
                    return None

                probabilidades = self._buscar_probabilidades(cursor, [sessao_id])[sessao_id]
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        return self._linha_para_entidade(linha, probabilidades)

    @staticmethod
    def _buscar_probabilidades(
        cursor: "pyodbc.Cursor", sessao_ids: list[int]
    ) -> dict[int, dict[str, float]]:
        """Busca, em uma única query, os scores por emoção de várias sessões
        (evita N+1 queries em ``listar_todas``). Garante as 7 chaves de
        ``EMOCOES_PT`` sempre presentes, mesmo que faltem linhas."""
        resultado: dict[int, dict[str, float]] = {
            sessao_id: {pt: 0.0 for pt in EMOCOES_PT} for sessao_id in sessao_ids
        }
        if not sessao_ids:
            return resultado

        placeholders = ",".join("?" for _ in sessao_ids)
        cursor.execute(
            f"""
            SELECT sc.sessao_id, e.codigo, sc.pontuacao
            FROM dbo.pontuacoes_emocao_sessao AS sc
            JOIN dbo.emocoes AS e ON e.id = sc.emocao_id
            WHERE sc.sessao_id IN ({placeholders})
            """,
            *sessao_ids,
        )
        for sessao_id, codigo, pontuacao in cursor.fetchall():
            resultado[sessao_id][codigo] = float(pontuacao)
        return resultado

    @staticmethod
    def _linha_para_entidade(linha: Any, probabilidades: dict[str, float]) -> Sessao:
        data_sessao = linha.data_sessao
        valor_data = (
            data_sessao.isoformat() if hasattr(data_sessao, "isoformat") else str(data_sessao)
        )
        return Sessao(
            id=linha.id,
            nome=linha.nome,
            arquivo_origem=linha.arquivo_origem,
            data=valor_data,
            duracao=linha.duracao,
            frames=linha.frames,
            predominante=linha.predominante,
            confianca=float(linha.confianca),
            probabilidades=probabilidades,
            linha_do_tempo=json.loads(linha.linha_do_tempo_json),
        )
