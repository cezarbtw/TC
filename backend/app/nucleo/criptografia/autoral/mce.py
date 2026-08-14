import hashlib
import hmac
from typing import Any

from app.dominio.emocao import EMOCOES_PT


VERSAO_MCE = 1


def aplicar_mce(dados: dict[str, Any], chave: bytes) -> dict[str, Any]:
    mapa = _mapa_emocoes(chave)
    mapa_inverso = {
        emocao: codigo
        for codigo, emocao in mapa.items()
    }

    return {
        "p": _codificar_distribuicao(
            dados["probabilidades"],
            mapa_inverso,
        ),
        "t": _codificar_linha_do_tempo(
            dados["linha_do_tempo"],
            mapa_inverso,
        ),
    }


def desfazer_mce(
    dados: dict[str, Any],
    chave: bytes,
) -> dict[str, Any]:
    mapa = _mapa_emocoes(chave)

    return {
        "probabilidades": _decodificar_distribuicao(
            dados["p"],
            mapa,
        ),
        "linha_do_tempo": _decodificar_linha_do_tempo(
            dados["t"],
            mapa,
        ),
    }


def _mapa_emocoes(chave: bytes) -> dict[str, str]:
    ordenadas = sorted(
        EMOCOES_PT,
        key=lambda emocao: hmac.new(
            chave,
            f"ordem:{emocao}".encode("utf-8"),
            hashlib.sha256,
        ).digest(),
    )

    return {
        f"e{indice + 1:02d}": emocao
        for indice, emocao in enumerate(ordenadas)
    }


def _codificar_distribuicao(
    distribuicao: dict[str, float],
    mapa_inverso: dict[str, str],
) -> dict[str, float]:
    return {
        mapa_inverso[emocao]: float(distribuicao[emocao])
        for emocao in EMOCOES_PT
    }


def _decodificar_distribuicao(
    distribuicao: dict[str, float],
    mapa: dict[str, str],
) -> dict[str, float]:
    return {
        emocao: float(distribuicao[codigo])
        for codigo, emocao in mapa.items()
    }


def _codificar_linha_do_tempo(
    linha_do_tempo: dict[str, list[float]],
    mapa_inverso: dict[str, str],
) -> dict[str, list[float]]:
    return {
        mapa_inverso[emocao]: [
            float(valor)
            for valor in linha_do_tempo[emocao]
        ]
        for emocao in EMOCOES_PT
    }


def _decodificar_linha_do_tempo(
    linha_do_tempo: dict[str, list[float]],
    mapa: dict[str, str],
) -> dict[str, list[float]]:
    return {
        emocao: [
            float(valor)
            for valor in linha_do_tempo[codigo]
        ]
        for codigo, emocao in mapa.items()
    }
