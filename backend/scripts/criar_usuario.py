"""Cria uma conta local. Execute a partir de backend/:

python scripts/criar_usuario.py usuario "Ana" --senha "uma-senha-forte"
"""
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.nucleo.autenticacao import gerar_hash_senha
from app.nucleo.configuracoes import obter_configuracoes
from app.persistencia.conexao import escopo_conexao


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria um usuário do EmotionLens.")
    parser.add_argument("usuario", help="Nome usado no login")
    parser.add_argument("nome_exibicao", help="Nome mostrado na aplicação")
    parser.add_argument("--senha", help="Senha inicial; se omitida, será solicitada")
    args = parser.parse_args()

    senha = args.senha or getpass.getpass("Senha inicial: ")
    if len(senha) < 12:
        parser.error("A senha deve ter pelo menos 12 caracteres.")

    with escopo_conexao(obter_configuracoes()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.usuarios (nome, nome_exibicao, senha_hash) VALUES (?, ?, ?)",
            args.usuario,
            args.nome_exibicao,
            gerar_hash_senha(senha),
        )
    print(f"Usuário '{args.usuario}' criado.")


if __name__ == "__main__":
    main()
