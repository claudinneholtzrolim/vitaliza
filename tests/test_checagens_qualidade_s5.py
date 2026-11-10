"""Regressões de cobertura e interpretação da revisão da entrega de Claudinne."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location('checagens', Path(__file__).resolve().parents[1] / 'src/checagens_qualidade_s5.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def entradas():
    n = 14753
    cols = dict(user_id=[f'u_{i:08x}' for i in range(n)], tempo_assinatura_dias=10,
                treinos_30d=1, treinos_90d=1, minutos_30d=30., minutos_90d=30.,
                dias_ativos_30d=1, dias_ativos_90d=1, proporcao_video_90d=1.,
                dias_desde_ultimo_treino_2026=2., sem_treino_observado_2026=0,
                nivel='iniciante', dias_planejados_semana=3)
    c = pd.DataFrame(cols)
    b = c.assign(plano='mensal', canal_cobranca='web_pix', ultima_cobranca_aprovada_reais=34.90,
                 receita_mensal_equivalente_proxy=34.90,
                 receita_liquida_mensal_equivalente_proxy=34.90 * (1 - .0099))
    return c, b


class ChecagensTests(unittest.TestCase):
    def test_reordenacao_nao_muda_cobertura(self):
        c, b = entradas()
        m.validar_entradas(c, b.iloc[::-1])

    def test_duplicata_que_set_esconde_e_rejeitada(self):
        c, b = entradas()
        c.loc[1, 'user_id'] = c.loc[0, 'user_id']
        with self.assertRaises(ValueError): m.validar_entradas(c, b)

    def test_chave_ausente(self):
        c, b = entradas()
        c.loc[0, 'user_id'] = None
        with self.assertRaises(ValueError): m.validar_entradas(c, b)

    def test_canal_desconhecido_nao_some_na_taxa(self):
        c, b = entradas()
        b.loc[0, 'canal_cobranca'] = 'desconhecido'
        with self.assertRaises(ValueError): m.validar_entradas(c, b)

    def test_financeiro_ausente_nao_e_silenciosamente_somado(self):
        c, b = entradas()
        b.loc[0, 'receita_liquida_mensal_equivalente_proxy'] = np.nan
        with self.assertRaises(ValueError): m.validar_entradas(c, b)

    def test_bases_com_mesmas_chaves_mas_valores_diferentes(self):
        c, b = entradas()
        b.loc[0, 'treinos_30d'] = 2
        with self.assertRaises(ValueError): m.validar_entradas(c, b)

    def test_freemium_nao_e_erro_de_qualidade(self):
        c, _ = entradas()
        c.loc[0, 'dias_desde_ultimo_treino_2026'] = 15
        flags = m.marcar(c)
        self.assertEqual(flags.loc[0, 'sinal_atividade_anterior_assinatura_paga'], 1)
        self.assertEqual(flags.loc[0, 'revisar'], 0)

    def test_sem_treino_preserva_pessoa_e_ausencia(self):
        c, _ = entradas()
        c.loc[0, ['treinos_30d','treinos_90d','minutos_30d','minutos_90d','dias_ativos_30d','dias_ativos_90d']] = 0
        c.loc[0, 'proporcao_video_90d'] = np.nan
        f = m.marcar(c)
        self.assertEqual(len(f), len(c))
        self.assertEqual(f.loc[0, 'sem_treino_90d'], 1)
        self.assertEqual(f.loc[0, 'revisar'], 0)


if __name__ == '__main__': unittest.main()
