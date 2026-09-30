"""Hash de senhas e criação/validação de tokens JWT."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.dominio.usuario import Usuario
from app.nucleo.configuracoes import Configuracoes


def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def senha_confere(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token(usuario: Usuario, configuracoes: Configuracoes) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=configuracoes.jwt_expiracao_minutos)
    return jwt.encode(
        {"sub": str(usuario.id), "exp": expiracao},
        configuracoes.chave_jwt,
        algorithm=configuracoes.algoritmo_jwt,
    )
