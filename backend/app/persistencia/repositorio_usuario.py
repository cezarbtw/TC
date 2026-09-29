"""Repositório de usuários locais cadastrados pelo administrador."""
from __future__ import annotations

from app.dominio.usuario import Usuario
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes


class RepositorioUsuario:
    def __init__(self, configuracoes: Configuracoes | None = None) -> None:
        self._configuracoes = configuracoes or obter_configuracoes()

    def obter_por_nome(self, nome: str) -> tuple[Usuario, str] | None:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nome, nome_exibicao, ativo, senha_hash
                    FROM dbo.usuarios
                    WHERE nome = ?
                    """,
                    nome,
                )
                linha = cursor.fetchone()
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        if linha is None:
            return None
        return (
            Usuario(
                id=linha.id,
                nome=linha.nome,
                nome_exibicao=linha.nome_exibicao,
                ativo=bool(linha.ativo),
            ),
            linha.senha_hash,
        )

    def obter_por_id(self, usuario_id: int) -> Usuario | None:
        import pyodbc

        from app.persistencia.conexao import escopo_conexao
        from app.persistencia.excecoes import traduzir_erro_pyodbc

        try:
            with escopo_conexao(self._configuracoes) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nome, nome_exibicao, ativo
                    FROM dbo.usuarios
                    WHERE id = ?
                    """,
                    usuario_id,
                )
                linha = cursor.fetchone()
        except pyodbc.Error as exc:
            raise traduzir_erro_pyodbc(exc) from exc

        if linha is None:
            return None
        return Usuario(
            id=linha.id,
            nome=linha.nome,
            nome_exibicao=linha.nome_exibicao,
            ativo=bool(linha.ativo),
        )
