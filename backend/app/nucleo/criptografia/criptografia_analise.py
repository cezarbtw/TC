import json
from typing import Any

from app.criptografia.mce.mce import (
    aplicar_mce,
    desfazer_mce,
    VERSAO_MCE,
)

from app.criptografia.aes.aes_gcm import (
    normalizar_chave_aes,
    criptografar_aes,
    descriptografar_aes,
    b64e,
    b64d,
)


VERSAO_CRIPTOGRAFIA = 1


class CriptografiaAnalise:

    def __init__(
        self,
        chave_aes: str,
        chave_mce: str,
    ) -> None:

        self._chave_aes = normalizar_chave_aes(chave_aes)
        self._chave_mce = chave_mce.encode("utf-8")

    def criptografar(
        self,
        dados: dict[str, Any],
    ) -> str:

        # 1ª CAMADA — MCE (AUTORAL)
        dados_mce = aplicar_mce(
            dados,
            self._chave_mce,
        )

        texto_mce = json.dumps(
            dados_mce,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        # 2ª CAMADA — AES-256-GCM
        associado = (
            f"emotionlens:v{VERSAO_CRIPTOGRAFIA}"
            .encode("utf-8")
        )

        nonce, texto_cifrado = criptografar_aes(
            texto_mce,
            self._chave_aes,
            associado,
        )

        envelope = {
            "v": VERSAO_CRIPTOGRAFIA,
            "alg": "AES-256-GCM",
            "mce": VERSAO_MCE,
            "nonce": b64e(nonce),
            "ct": b64e(texto_cifrado),
        }

        return json.dumps(
            envelope,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def descriptografar(
        self,
        envelope_json: str,
    ) -> dict[str, Any]:

        envelope = json.loads(envelope_json)

        if envelope.get("v") != VERSAO_CRIPTOGRAFIA:
            raise ValueError(
                "Versão de criptografia não suportada."
            )

        if envelope.get("alg") != "AES-256-GCM":
            raise ValueError(
                "Algoritmo de criptografia não suportado."
            )

        if envelope.get("mce") != VERSAO_MCE:
            raise ValueError(
                "Versão MCE não suportada."
            )

        associado = (
            f"emotionlens:v{VERSAO_CRIPTOGRAFIA}"
            .encode("utf-8")
        )

        # 1º — remove AES
        texto_mce = descriptografar_aes(
            b64d(envelope["ct"]),
            b64d(envelope["nonce"]),
            self._chave_aes,
            associado,
        )

        dados_mce = json.loads(
            texto_mce.decode("utf-8")
        )

        # 2º — desfaz transformação autoral
        return desfazer_mce(
            dados_mce,
            self._chave_mce,
        )
