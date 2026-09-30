import json
import unittest

from app.nucleo.criptografia.autoral.mce import aplicar_mce, desfazer_mce
from app.nucleo.criptografia.criptografia_analise import CriptografiaAnalise


DADOS_ANALISE = {
    "probabilidades": {
        "feliz": 71.5,
        "triste": 5.0,
        "raiva": 4.5,
        "surpresa": 8.0,
        "medo": 3.0,
        "nojo": 2.0,
        "neutro": 6.0,
    },
    "linha_do_tempo": {
        "feliz": [70.0, 73.0],
        "triste": [4.0, 6.0],
        "raiva": [3.0, 6.0],
        "surpresa": [7.0, 9.0],
        "medo": [2.0, 4.0],
        "nojo": [1.0, 3.0],
        "neutro": [5.0, 7.0],
    },
}


class CriptografiaAnaliseTest(unittest.TestCase):
    def test_mce_substitui_apenas_chaves_de_emocao(self) -> None:
        dados_codificados = aplicar_mce(DADOS_ANALISE)

        self.assertEqual(set(dados_codificados), {"probabilidades", "linha_do_tempo"})
        self.assertEqual(dados_codificados["probabilidades"]["T1975"], 71.5)
        self.assertEqual(dados_codificados["linha_do_tempo"]["T1975"], [70.0, 73.0])
        self.assertEqual(desfazer_mce(dados_codificados), DADOS_ANALISE)

    def test_criptografia_restaura_a_analise(self) -> None:
        criptografia = CriptografiaAnalise("chave-de-teste")

        envelope_json = criptografia.criptografar(DADOS_ANALISE)

        self.assertNotIn("feliz", envelope_json)
        self.assertEqual(criptografia.descriptografar(envelope_json), DADOS_ANALISE)

    def test_envelope_nao_inclui_versao_mce(self) -> None:
        criptografia = CriptografiaAnalise("chave-de-teste")
        envelope = json.loads(criptografia.criptografar(DADOS_ANALISE))

        self.assertNotIn("mce", envelope)
