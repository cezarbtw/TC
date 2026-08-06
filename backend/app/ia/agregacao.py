"""Regras de agregação de emoções ao longo de um vídeo.

Funções puras (sem I/O), testáveis isoladamente. Recebem distribuições por frame
(já em português) e produzem os campos consumidos pelo dashboard.
"""
from __future__ import annotations

from app.dominio.emocao import EMOCOES_PT


def _arredondar1(valor: float) -> float:
    return round(float(valor), 1)


def media_probabilidades(distribuicoes: list[dict[str, float]]) -> dict[str, float]:
    """Média por emoção sobre todos os frames, arredondada a 1 casa.

    Sempre retorna as sete emoções em português, na ordem canônica.
    """
    if not distribuicoes:
        return {emocao: 0.0 for emocao in EMOCOES_PT}

    totais = {emocao: 0.0 for emocao in EMOCOES_PT}
    for frame in distribuicoes:
        for emocao in EMOCOES_PT:
            totais[emocao] += float(frame.get(emocao, 0.0))

    quantidade = len(distribuicoes)
    return {emocao: _arredondar1(totais[emocao] / quantidade) for emocao in EMOCOES_PT}


def emocao_predominante(probabilidades: dict[str, float]) -> tuple[str, float]:
    """Retorna (emoção predominante, confiança). Empate resolve pela ordem PT."""
    predominante = max(EMOCOES_PT, key=lambda e: probabilidades.get(e, 0.0))
    return predominante, _arredondar1(probabilidades.get(predominante, 0.0))


def suavizar_distribuicoes(
    distribuicoes: list[dict[str, float]], janela: int
) -> list[dict[str, float]]:
    """Suavização temporal por média móvel centrada (janela ``janela``).

    Reduz ruído/oscilação da classificação quadro a quadro, preservando o número
    de pontos (comprimento da série). Janela <= 1 ou série curta: retorna cópia.
    """
    quantidade = len(distribuicoes)
    if janela <= 1 or quantidade == 0:
        return [dict(frame) for frame in distribuicoes]

    metade = janela // 2
    suavizadas: list[dict[str, float]] = []
    for i in range(quantidade):
        inicio = max(0, i - metade)
        fim = min(quantidade, i + metade + 1)
        trecho = distribuicoes[inicio:fim]
        media = {
            emocao: sum(frame.get(emocao, 0.0) for frame in trecho) / len(trecho)
            for emocao in EMOCOES_PT
        }
        suavizadas.append(media)
    return suavizadas


def confianca_media(distribuicoes: list[dict[str, float]]) -> float:
    """Confiança média da sessão: média da maior probabilidade de cada frame."""
    if not distribuicoes:
        return 0.0
    picos = [max(frame.get(e, 0.0) for e in EMOCOES_PT) for frame in distribuicoes]
    return _arredondar1(sum(picos) / len(picos))


def construir_linha_do_tempo(distribuicoes: list[dict[str, float]]) -> dict[str, list[float]]:
    """Transpõe as distribuições por frame em séries por emoção.

    Resultado: ``{ "feliz": [v0, v1, ...], "triste": [...], ... }``.
    """
    return {
        emocao: [_arredondar1(frame.get(emocao, 0.0)) for frame in distribuicoes]
        for emocao in EMOCOES_PT
    }
