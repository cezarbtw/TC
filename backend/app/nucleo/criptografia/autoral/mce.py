from typing import Any

TABELA_SUBSTITUICAO = {
    "A": "N",
    "N": "A",
    "O": "B",
    "B": "O",
    "C": "P",
    "P": "C",
    "D": "Q",
    "Q": "D",
    "E": "1",
    "1": "E",
    "F": "T",
    "T": "F",
    "G": "2",
    "2": "G",
    "S": "H",
    "H": "S",
    "U": "8",
    "8": "U",
    "I": "7",
    "7": "I",
    "V": "J",
    "J": "V",
    "W": "4",
    "4": "W",
    "L": "9",
    "9": "L",
    "M": "Y",
    "Y": "M",
    "K": "3",
    "3": "K",
    "X": "6",
    "6": "X",
    "Z": "5",
    "5": "Z",
}


def _substituir(texto: str) -> str:
    return "".join(
        TABELA_SUBSTITUICAO.get(caractere, caractere)
        for caractere in texto.upper()
    )


def aplicar_mce(dados: dict[str, Any]) -> dict[str, Any]:
    return {
        "probabilidades": {
            _substituir(emocao): float(valor)
            for emocao, valor in dados["probabilidades"].items()
        },
        "linha_do_tempo": {
            _substituir(emocao): [
                float(valor)
                for valor in valores
            ]
            for emocao, valores in dados["linha_do_tempo"].items()
        },
    }


def desfazer_mce(dados: dict[str, Any]) -> dict[str, Any]:
    return {
        "probabilidades": {
            _substituir(codigo).lower(): float(valor)
            for codigo, valor in dados["probabilidades"].items()
        },
        "linha_do_tempo": {
            _substituir(codigo).lower(): [
                float(valor)
                for valor in valores
            ]
            for codigo, valores in dados["linha_do_tempo"].items()
        },
    }
