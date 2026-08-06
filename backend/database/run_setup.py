"""Executa os scripts de setup do banco (create_database, create_tables,
constraints, indexes, seed), na ordem correta, usando as mesmas variáveis de
conexão do backend (``EMOTIONLENS_DB_*`` no ``.env``).

Uso (a partir da pasta backend/, com o venv ativado e pyodbc instalado):

    python database/run_setup.py

Idempotente: os scripts usam ``IF NOT EXISTS``/``MERGE``, então rodar de novo
não duplica nem falha.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.nucleo.configuracoes import obter_configuracoes  # noqa: E402
from app.persistencia.conexao import _construir_string_conexao  # noqa: E402

SCRIPTS = [
    "create_database.sql",
    "create_tables.sql",
    "constraints.sql",
    "indexes.sql",
    "seed.sql",
]

BATCH_SEPARATOR = re.compile(r"(?im)^\s*GO\s*$")


def main() -> None:
    import pyodbc

    configuracoes = obter_configuracoes()
    # Conecta em 'master' (o banco alvo ainda pode não existir); os próprios
    # scripts fazem "USE ..." para trocar de contexto.
    configuracoes_master = configuracoes.model_copy(update={"db_banco": "master"})
    string_conexao = _construir_string_conexao(configuracoes_master)

    print(
        f"Conectando em {configuracoes.db_servidor} "
        f"(Trusted={configuracoes.db_conexao_confiavel})..."
    )
    conn = pyodbc.connect(string_conexao, autocommit=True)  # autocommit: CREATE DATABASE exige
    cursor = conn.cursor()

    base_dir = Path(__file__).resolve().parent
    try:
        for script_name in SCRIPTS:
            content = (base_dir / script_name).read_text(encoding="utf-8")
            batches = [b.strip() for b in BATCH_SEPARATOR.split(content) if b.strip()]
            print(f"=== {script_name} ({len(batches)} lote(s)) ===")
            for i, batch in enumerate(batches, start=1):
                cursor.execute(batch)
                while cursor.nextset():
                    pass
                print(f"  lote {i}: OK")
    except pyodbc.Error as exc:
        print(f"\nERRO ao executar os scripts: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

    print(f"\nBanco '{configuracoes.db_banco}' configurado com sucesso em {configuracoes.db_servidor}.")


if __name__ == "__main__":
    main()
