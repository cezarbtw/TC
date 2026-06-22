"""
Configuração do banco de dados SQLite com sqlite3 puro.
Sem ORM externo — simples, leve e ideal para um TCC.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "emotionlens.db"


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com Row Factory para acessar colunas por nome."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas se ainda não existirem."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                filename    TEXT    NOT NULL,
                date        TEXT    NOT NULL,           -- YYYY-MM-DD
                duration    TEXT    NOT NULL,           -- MM:SS
                frames      INTEGER NOT NULL,
                predominant TEXT    NOT NULL,
                confidence  REAL    NOT NULL,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS emotion_probabilities (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                emotion     TEXT    NOT NULL,
                probability REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS timeline_points (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                second_idx  INTEGER NOT NULL,
                emotion     TEXT    NOT NULL,
                value       REAL    NOT NULL
            );
        """)
    print("✅ Banco de dados inicializado.")
