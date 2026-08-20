import json
from typing import Any

from app.nucleo.criptografia.autoral.mce import (
    aplicar_mce,
    desfazer_mce,
)

from app.nucleo.criptografia.padrao.aes_gcm import (
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
    ) -> None:

        self._chave_aes = normalizar_chave_aes(chave_aes)

    def criptografar(
        self,
        dados: dict[str, Any],
    ) -> str:

        # 1ª CAMADA — substitui os nomes das emoções.
        dados_mce = aplicar_mce(dados)

        texto_mce = json.dumps(
            dados_mce,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        # 2ª CAMADA — AES-256-GCM.
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

        associado = (
            f"emotionlens:v{VERSAO_CRIPTOGRAFIA}"
            .encode("utf-8")
        )

        # 1ª etapa — remove AES.
        texto_mce = descriptografar_aes(
            b64d(envelope["ct"]),
            b64d(envelope["nonce"]),
            self._chave_aes,
            associado,
        )

        dados_mce = json.loads(
            texto_mce.decode("utf-8")
        )

        # 2ª etapa — restaura os nomes das emoções.
        return desfazer_mce(dados_mce)
