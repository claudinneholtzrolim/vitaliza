"""Casos sintéticos: classificador de motivações, cenário de aniversários e recálculo independente."""
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calcular_risco_janela_s5 import aniversario_2026, aniversario_na_janela, tabela_risco
from conferencia_comum_s5 import atividades_do_usuario, bate, when
from personas_regras_s5 import NAO_CLASSIFICADO, estado_objetivo, meta_com_data, norm, tema_principal


def tema(texto):
    return tema_principal(norm(texto))


class ClassificadorMotivacoesTests(unittest.TestCase):
    def test_estado_nulo_sem_conteudo_e_com_conteudo(self):
        self.assertEqual(estado_objetivo(None), "nulo")
        self.assertEqual(estado_objetivo(float("nan")), "nulo")
        self.assertEqual(estado_objetivo("   "), "nulo")
        for texto in ["nada", ".", "OK", "Não sei", "ab", "sla"]:
            self.assertEqual(estado_objetivo(texto), "sem conteúdo", texto)
        self.assertEqual(estado_objetivo("Baixar o colesterol"), "com conteúdo")

    def test_um_tema_por_resposta_na_ordem_de_prioridade(self):
        self.assertEqual(tema("Achar uma galera pra correr"), "companhia / social")
        # companhia vem antes de desempenho, mesmo com "correr mais"
        self.assertEqual(tema("treinar com o pessoal do trabalho para correr mais rapido"), "companhia / social")
        # "saúde mental" é mente/bem-estar, e não saúde clínica
        self.assertEqual(tema("Cuidar da saúde mental"), "mente / bem-estar")
        self.assertEqual(tema("Meu médico mandou eu me mexer"), "saúde clínica")
        self.assertEqual(tema("Baixar meu tempo nos 10k"), "desempenho")
        self.assertEqual(tema("Emagrecer e me sentir bem no espelho"), "estética / peso")

    def test_erros_de_digitacao_conhecidos_e_nao_classificado(self):
        self.assertEqual(tema("dorimr melhor"), "mente / bem-estar")
        self.assertEqual(tema("controlar a prsesao"), "saúde clínica")
        self.assertEqual(tema("secar ab arriga"), NAO_CLASSIFICADO)

    def test_meta_com_data_e_sinalizador_a_parte(self):
        t = norm("Perder peso. Tenho o casamento da minha irmã daqui uns 6 meses")
        self.assertEqual(tema_principal(t), "estética / peso")
        self.assertTrue(meta_com_data(t))
        self.assertFalse(meta_com_data(norm("Perder peso")))
        self.assertTrue(meta_com_data(norm("Subir de nível no pedal, tenho um 5k dia 4/03")))


class AniversarioNaJanelaTests(unittest.TestCase):
    def test_29_de_fevereiro_vira_28(self):
        self.assertEqual(aniversario_2026("2024-02-29"), pd.Timestamp("2026-02-28"))
        self.assertEqual(aniversario_2026("2022-10-15"), pd.Timestamp("2026-10-15"))

    def test_extremos_da_janela_sao_incluidos(self):
        self.assertTrue(aniversario_na_janela("anual", "2022-10-01"))
        self.assertTrue(aniversario_na_janela("anual", "2022-11-29"))
        self.assertFalse(aniversario_na_janela("anual", "2022-09-30"))
        self.assertFalse(aniversario_na_janela("anual", "2022-11-30"))

    def test_inicio_antigo_nao_e_perdido(self):
        # o rascunho antigo olhava só 3 anos adiante e perdia este caso (início há mais de 4 anos)
        self.assertTrue(aniversario_na_janela("anual", "2020-10-20"))

    def test_plano_mensal_nao_entra(self):
        self.assertFalse(aniversario_na_janela("mensal", "2022-10-15"))

    def test_inicio_em_2026_antes_da_janela_nao_entra(self):
        self.assertFalse(aniversario_na_janela("anual", "2026-03-01"))

    def test_tabela_por_segmento(self):
        seg = pd.DataFrame({
            "user_id": ["a", "b", "c", "d"], "segmento": [0, 0, 0, 3],
            "plano": ["anual", "mensal", "anual", "anual"],
            "renovacao_desligada_retrato": [1, 1, 1, 0],
            "receita_liquida_mensal_equivalente_proxy": [10.0, 5.0, 7.0, 3.0],
            "sem_treino_90d": [1, 0, 0, 0]})
        ativas = pd.DataFrame({
            "user_id": ["a", "b", "c", "d"],
            "inicio": pd.to_datetime(["2021-10-20", "2022-10-20", "2022-12-20", "2022-10-20"]),
            "renovacao_automatica": ["nao", "nao", "nao", "sim"]})
        _, t = tabela_risco(seg, ativas)
        ad = t.loc["Adormecidos"]
        self.assertEqual(ad["renov_desligada_n"], 3)
        self.assertEqual(ad["mensal_renov_desligada_n"], 1)
        self.assertEqual(ad["anuais_aniversario_na_janela_e_renov_desligada_n"], 1)
        self.assertAlmostEqual(ad["anuais_aniversario_na_janela_e_renov_desligada_receita"], 10.0)
        # o anual "d" tem aniversário na janela, mas a renovação está ligada: conta como aniversário, não como desligado
        self.assertEqual(t.loc["Novatos", "anuais_com_aniversario_na_janela_n"], 1)
        self.assertEqual(t.loc["Novatos", "anuais_aniversario_na_janela_e_renov_desligada_n"], 0)


class RecalculoIndependenteTests(unittest.TestCase):
    def test_utc_cruza_a_data_em_brasilia(self):
        self.assertEqual(when("2026-10-01T02:00:00Z"), pd.Timestamp("2026-09-30 23:00:00").to_pydatetime())

    def test_copia_do_app_removida_apos_corrigir_o_fuso_do_garmin(self):
        linhas = [
            dict(atividade_id="g", user_id="x", origem="garmin", inicio="2026-09-30 15:00:00", tipo="forca", duracao_min=30.0),
            dict(atividade_id="c", user_id="x", origem="app", inicio="2026-09-30 12:03:00", tipo="forca", duracao_min=30.0),
            dict(atividade_id="o", user_id="x", origem="app", inicio="2026-09-29 12:00:00", tipo="strength", duracao_min=45.0),
            dict(atividade_id="z", user_id="x", origem="app", inicio="2026-09-28 12:00:00", tipo="run", duracao_min=0.0),
        ]
        _, m = atividades_do_usuario(linhas)
        self.assertEqual(m["copias_removidas"], 1)
        self.assertEqual(m["duracao_zero"], 1)
        self.assertEqual(m["dias_ativos_90d"], 2)
        self.assertEqual(m["min_por_treino_90d"], 37.5)
        self.assertEqual(m["proporcao_video_90d"], 1)
        self.assertEqual(m["recencia_dias"], 0.5)
        self.assertEqual(m["treinos_30d"] - m["treinos_30d_anteriores"], 2)

    def test_sem_treino_valido_nao_imputa_recencia(self):
        _, m = atividades_do_usuario([])
        self.assertIsNone(m["recencia_dias"])
        self.assertIsNone(m["proporcao_video_90d"])

    def test_tolerancia_nao_esconde_ausencia_estrutural(self):
        self.assertTrue(bate(None, np.nan, 0))
        self.assertFalse(bate(None, 273, 1))
        self.assertTrue(bate(98, 97, 1))
        self.assertFalse(bate(99, 97, 1))
        self.assertTrue(bate("anual", "anual", None))
        self.assertFalse(bate("anual", "mensal", None))


if __name__ == "__main__":
    unittest.main()
