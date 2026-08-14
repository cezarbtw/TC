import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def normalizar_chave_aes(chave: str) -> bytes:
    try:
        decodificada = base64.urlsafe_b64decode(
            chave.encode("utf-8")
        )

        if len(decodificada) == 32:
            return decodificada

    except Exception:
        pass

    return hashlib.sha256(
        chave.encode("utf-8")
    ).digest()


def criptografar_aes(
    dados: bytes,
    chave: bytes,
    associado: bytes,
) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)

    cifrador = AESGCM(chave)

    texto_cifrado = cifrador.encrypt(
        nonce,
        dados,
        associado,
    )

    return nonce, texto_cifrado


def descriptografar_aes(
    texto_cifrado: bytes,
    nonce: bytes,
    chave: bytes,
    associado: bytes,
) -> bytes:
    cifrador = AESGCM(chave)

    return cifrador.decrypt(
        nonce,
        texto_cifrado,
        associado,
    )


def b64e(valor: bytes) -> str:
    return base64.urlsafe_b64encode(valor).decode("ascii")


def b64d(valor: str) -> bytes:
    return base64.urlsafe_b64decode(valor.encode("ascii"))
