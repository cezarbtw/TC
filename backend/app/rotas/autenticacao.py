"""Login de usuários locais previamente cadastrados."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dominio.usuario import Usuario
from app.esquemas.autenticacao import TokenSchema, UsuarioSchema
from app.nucleo.autenticacao import criar_token, senha_confere
from app.nucleo.configuracoes import Configuracoes, obter_configuracoes
from app.rotas.dependencias import obter_usuario_atual, obter_repositorio_usuario

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenSchema, summary="Autentica um usuário cadastrado")
async def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    repositorio=Depends(obter_repositorio_usuario),
    configuracoes: Configuracoes = Depends(obter_configuracoes),
) -> TokenSchema:
    encontrado = repositorio.obter_por_nome(formulario.username)
    if encontrado is None:
        raise _credenciais_invalidas()
    usuario, senha_hash = encontrado
    if not usuario.ativo or not senha_confere(formulario.password, senha_hash):
        raise _credenciais_invalidas()
    return TokenSchema(access_token=criar_token(usuario, configuracoes))


@router.get("/me", response_model=UsuarioSchema, summary="Retorna o usuário autenticado")
async def me(usuario: Usuario = Depends(obter_usuario_atual)) -> UsuarioSchema:
    return UsuarioSchema(id=usuario.id, username=usuario.nome, display_name=usuario.nome_exibicao)


def _credenciais_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha inválidos.",
        headers={"WWW-Authenticate": "Bearer"},
    )
