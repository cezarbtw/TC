"""Serviço: análise emocional de um vídeo de sessão (POST /sessions/upload).

Pipeline (HSEmotion):
  1. Amostra frames do vídeo a ~fps_alvo (não processa todos os frames).
  2. Para cada frame, detecta/alinha/classifica via AnalisadorEmocaoHSEmotion.
  3. Ignora frames sem face válida (detector já filtra confiança/tamanho).
  4. Aplica suavização temporal (média móvel) às distribuições por frame.
  5. Agrega em uma Sessao no MESMO formato consumido pelo dashboard.
"""
from __future__ import annotations

from datetime import date

from app.dominio.emocao import EmocaoFace, traduzir_scores_para_pt
from app.dominio.sessao import RascunhoSessao
from app.esquemas.sessao import SessaoSchema
from app.ia import agregacao as agg
from app.nucleo.erros import NenhumaFaceDetectadaError
from app.nucleo.logs import obter_logger
from app.servicos.servico_sessao import sessao_para_schema

logger = obter_logger(__name__)


class ServicoAnaliseSessao:
    def __init__(
        self,
        extrator,
        analisador,
        repositorio,
        fps_alvo: float,
        max_frames: int,
        janela_suavizacao: int,
    ) -> None:
        self._extrator = extrator
        self._analisador = analisador
        self._repositorio = repositorio
        self._fps_alvo = fps_alvo
        self._max_frames = max_frames
        self._janela_suavizacao = janela_suavizacao

    def executar(self, caminho_video: str, arquivo_origem: str) -> SessaoSchema:
        frames, meta = self._extrator.extrair(
            caminho_video, self._fps_alvo, self._max_frames
        )

        # Distribuição (em PT) por frame com face válida. O detector (YOLOv8) já
        # descarta faces com baixa confiança ou tamanho insuficiente.
        distribuicoes: list[dict[str, float]] = []
        for frame in frames:
            faces = self._analisador.analisar_faces(frame)
            if not faces:
                continue
            principal = max(faces, key=_pontuacao_face)  # face principal (maior/mais confiável)
            distribuicoes.append(traduzir_scores_para_pt(principal.pontuacoes))

        if not distribuicoes:
            raise NenhumaFaceDetectadaError(
                "Nenhuma face foi detectada nos frames analisados do vídeo."
            )

        # Suavização temporal antes de agregar/plotar a timeline.
        suavizadas = agg.suavizar_distribuicoes(distribuicoes, self._janela_suavizacao)

        probabilidades = agg.media_probabilidades(suavizadas)
        predominante, _ = agg.emocao_predominante(probabilidades)
        confianca = agg.confianca_media(suavizadas)
        linha_do_tempo = agg.construir_linha_do_tempo(suavizadas)

        rascunho = RascunhoSessao(
            arquivo_origem=arquivo_origem,
            data=date.today().isoformat(),
            duracao=meta.rotulo_duracao,
            frames=meta.total_frames or len(distribuicoes),
            predominante=predominante,
            confianca=confianca,
            probabilidades=probabilidades,
            linha_do_tempo=linha_do_tempo,
        )
        sessao = self._repositorio.criar(rascunho)
        logger.info(
            "Sessão %s criada a partir de '%s': predominante=%s (%.1f%%), "
            "%d frames com face de %d amostrados.",
            sessao.id,
            arquivo_origem,
            predominante,
            confianca,
            len(distribuicoes),
            len(frames),
        )
        return sessao_para_schema(sessao)


def _pontuacao_face(face: EmocaoFace) -> tuple[int, float]:
    """Critério de seleção da face principal: maior área e, em empate, maior
    confiança de detecção."""
    area = face.regiao.area if face.regiao else 0
    return area, face.confianca_deteccao
