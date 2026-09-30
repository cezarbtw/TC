"""Criptografia em duas camadas para os dados de análise emocional.

Camada autoral (MCE - Mapeamento Criptográfico Emocional): transforma a
estrutura emocional antes da criptografia principal, renomeando emoções,
reordenando chaves e aplicando pequenos deltas reversíveis nos valores
numéricos.

Camada pronta: AES-256-GCM, via biblioteca ``cryptography``.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.dominio.emocao import EMOCOES_PT


VERSAO_CRIPTOGRAFIA = 1
VERSAO_MCE = 1


class CriptografiaAnalise:
    def __init__(self, chave_aes: str, chave_mce: str) -> None:
        self._chave_aes = _normalizar_chave_aes(chave_aes)
        self._chave_mce = chave_mce.encode("utf-8")

    def criptografar(self, dados: dict[str, Any]) -> str:
        dados_mce = _aplicar_mce(dados, self._chave_mce)
        texto_mce = json.dumps(
            dados_mce,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        nonce = os.urandom(12)
        cifrador = AESGCM(self._chave_aes)
        associado = f"emotionlens:v{VERSAO_CRIPTOGRAFIA}".encode("utf-8")
        texto_cifrado = cifrador.encrypt(nonce, texto_mce, associado)

        envelope = {
            "v": VERSAO_CRIPTOGRAFIA,
            "alg": "AES-256-GCM",
            "mce": VERSAO_MCE,
            "nonce": _b64e(nonce),
            "ct": _b64e(texto_cifrado),
        }
        return json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))

    def descriptografar(self, envelope_json: str) -> dict[str, Any]:
        envelope = json.loads(envelope_json)
        if envelope.get("v") != VERSAO_CRIPTOGRAFIA:
            raise ValueError("Versão de criptografia não suportada.")
        if envelope.get("alg") != "AES-256-GCM":
            raise ValueError("Algoritmo de criptografia não suportado.")
        if envelope.get("mce") != VERSAO_MCE:
            raise ValueError("Versão MCE não suportada.")

        nonce = _b64d(envelope["nonce"])
        texto_cifrado = _b64d(envelope["ct"])
        associado = f"emotionlens:v{VERSAO_CRIPTOGRAFIA}".encode("utf-8")
        texto_mce = AESGCM(self._chave_aes).decrypt(nonce, texto_cifrado, associado)
        dados_mce = json.loads(texto_mce.decode("utf-8"))
        return _desfazer_mce(dados_mce, self._chave_mce)


def _normalizar_chave_aes(chave: str) -> bytes:
    try:
        decodificada = base64.urlsafe_b64decode(chave.encode("utf-8"))
        if len(decodificada) == 32:
            return decodificada
    except Exception:
        pass
    return hashlib.sha256(chave.encode("utf-8")).digest()


def _aplicar_mce(dados: dict[str, Any], chave: bytes) -> dict[str, Any]:
    mapa = _mapa_emocoes(chave)
    mapa_inverso = {emocao: codigo for codigo, emocao in mapa.items()}
    deltas = _deltas(chave)
    return {
        "p": _codificar_distribuicao(dados["probabilidades"], mapa_inverso, deltas),
        "t": _codificar_linha_do_tempo(dados["linha_do_tempo"], mapa_inverso, deltas),
    }


def _desfazer_mce(dados: dict[str, Any], chave: bytes) -> dict[str, Any]:
    mapa = _mapa_emocoes(chave)
    deltas = _deltas(chave)
    return {
        "probabilidades": _decodificar_distribuicao(dados["p"], mapa, deltas),
        "linha_do_tempo": _decodificar_linha_do_tempo(dados["t"], mapa, deltas),
    }


def _mapa_emocoes(chave: bytes) -> dict[str, str]:
    ordenadas = sorted(
        EMOCOES_PT,
        key=lambda emocao: hmac.new(chave, f"ordem:{emocao}".encode("utf-8"), hashlib.sha256).digest(),
    )
    return {f"e{indice + 1:02d}": emocao for indice, emocao in enumerate(ordenadas)}


def _deltas(chave: bytes) -> dict[str, float]:
    resultado: dict[str, float] = {}
    for emocao in EMOCOES_PT:
        digest = hmac.new(chave, f"delta:{emocao}".encode("utf-8"), hashlib.sha256).digest()
        inteiro = int.from_bytes(digest[:2], "big")
        resultado[emocao] = round(((inteiro % 101) - 50) / 100.0, 2)
    return resultado


def _codificar_distribuicao(
    distribuicao: dict[str, float], mapa_inverso: dict[str, str], deltas: dict[str, float]
) -> dict[str, float]:
    return {
        mapa_inverso[emocao]: _limitar(float(distribuicao[emocao]) + deltas[emocao])
        for emocao in EMOCOES_PT
    }


def _decodificar_distribuicao(
    distribuicao: dict[str, float], mapa: dict[str, str], deltas: dict[str, float]
) -> dict[str, float]:
    return {
        emocao: _limitar(float(distribuicao[codigo]) - deltas[emocao])
        for codigo, emocao in mapa.items()
    }


def _codificar_linha_do_tempo(
    linha_do_tempo: dict[str, list[float]], mapa_inverso: dict[str, str], deltas: dict[str, float]
) -> dict[str, list[float]]:
    return {
        mapa_inverso[emocao]: [_limitar(float(valor) + deltas[emocao]) for valor in linha_do_tempo[emocao]]
        for emocao in EMOCOES_PT
    }


def _decodificar_linha_do_tempo(
    linha_do_tempo: dict[str, list[float]], mapa: dict[str, str], deltas: dict[str, float]
) -> dict[str, list[float]]:
    return {
        emocao: [_limitar(float(valor) - deltas[emocao]) for valor in linha_do_tempo[codigo]]
        for codigo, emocao in mapa.items()
    }


def _limitar(valor: float) -> float:
    return round(valor, 2)


def _b64e(valor: bytes) -> str:
    return base64.urlsafe_b64encode(valor).decode("ascii")


def _b64d(valor: str) -> bytes:
    return base64.urlsafe_b64decode(valor.encode("ascii"))
