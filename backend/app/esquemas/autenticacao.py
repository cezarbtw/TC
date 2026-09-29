"""Contratos públicos da autenticação."""
from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioSchema(BaseModel):
    id: int
    username: str
    display_name: str
