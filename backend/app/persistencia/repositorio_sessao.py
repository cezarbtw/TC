"""Repositório de sessões persistido em SQL Server (pyodbc puro, sem ORM).

Todas as queries são parametrizadas (``?``) para evitar SQL Injection;
nenhuma entrada do usuário é concatenada diretamente em SQL.
"""
from __future__ import annotations

from datetime import date as date_type
from typing import TYPE_CHECKING, Any

from app.dominio.sessao import RascunhoSessao, Sessao
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.nucleo.criptografia import CriptografiaAnalise

if TYPE_CHECKING:
    import pyodbc


class RepositorioSessao:
    def __init__(self, configuracoes: Configuracoes | None = None) -> None:
        self._configuracoes = configuracoes or obter_configuracoes()
        self._criptografia = CriptografiaAnalise(
            self._configuracoes.chave_criptografia,
            self._configuracoes.chave_mce,
        )

    def criar(self, rascunho: RascunhoSessao) -> Sessao:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        analise_criptografada = self._criptografia.criptografar(
            {
                "probabilidades": rascunho.probabilidades,
                "linha_do_tempo": rascunho.linha_do_tempo,
            }
        )
        data_sessao = date_type.fromisoformat(rascunho.data)

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO dbo.sessoes
                        (nome, arquivo_origem, data_sessao, duracao, frames,
                         emocao_predominante_id, confianca, analise_criptografada)
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
                    analise_criptografada,
                )
                sessao_id = cursor.fetchone()[0]

                nome = f"Sessão {sessao_id:02d}"
                cursor.execute(
                    "UPDATE dbo.sessoes SET nome = ? WHERE id = ?",
                    nome,
                    sessao_id,
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
                           s.frames, e.codigo AS predominante, s.confianca,
                           s.analise_criptografada
                    FROM dbo.sessoes AS s
                    JOIN dbo.emocoes AS e ON e.id = s.emocao_predominante_id
                    WHERE s.excluido_em IS NULL
                    ORDER BY s.id DESC
                    """
                )
                linhas = cursor.fetchall()
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        return [self._linha_para_entidade(linha) for linha in linhas]

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
                           s.frames, e.codigo AS predominante, s.confianca,
                           s.analise_criptografada
                    FROM dbo.sessoes AS s
                    JOIN dbo.emocoes AS e ON e.id = s.emocao_predominante_id
                    WHERE s.id = ? AND s.excluido_em IS NULL
                    """,
                    sessao_id,
                )
                linha = cursor.fetchone()
                if linha is None:
                    return None
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        return self._linha_para_entidade(linha)

    def _linha_para_entidade(self, linha: Any) -> Sessao:
        data_sessao = linha.data_sessao
        valor_data = (
            data_sessao.isoformat() if hasattr(data_sessao, "isoformat") else str(data_sessao)
        )
        analise = self._criptografia.descriptografar(linha.analise_criptografada)
        return Sessao(
            id=linha.id,
            nome=linha.nome,
            arquivo_origem=linha.arquivo_origem,
            data=valor_data,
            duracao=linha.duracao,
            frames=linha.frames,
            predominante=linha.predominante,
            confianca=float(linha.confianca),
            probabilidades=analise["probabilidades"],
            linha_do_tempo=analise["linha_do_tempo"],
        )
