"""Casos sintéticos de tolerância, fuso, deduplicação e ausência estrutural."""
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from revisar_personas_kiril_s5 import agrees, cents, independent_metrics, local_time


class RevisaoPersonasTests(unittest.TestCase):
    def raw(self, activities):
        uid = "cliente_sintetico"
        return {
            "usuarios": pd.DataFrame([{"user_id": uid, "data_cadastro": "2026-09-01 10:00:00"}]),
            "assinaturas": pd.DataFrame([{"user_id": uid, "status_atual": "ativa", "inicio": "2026-09-08",
                "plano_atual": "anual", "canal_cobranca": "app_store", "renovacao_automatica": "nao"}]),
            "atividades": pd.DataFrame(activities, columns=["user_id", "origem", "inicio", "tipo", "duracao_min"]),
            "pagamentos": pd.DataFrame([{"user_id": uid, "status": "aprovado", "data_hora": "2026-09-08T03:00:00Z",
                "valor": "R$ 239,90", "metodo": "app_store"}]),
            "onboarding": pd.DataFrame(columns=["user_id", "respondido_em", "nivel"]),
            "amizades": pd.DataFrame(columns=["seguido_id", "desde"]),
            "feed_posts": pd.DataFrame(columns=["user_id", "data_hora"]),
            "tickets_suporte": pd.DataFrame(columns=["user_id", "aberto_em"]),
        }

    def test_local_time_crosses_date_boundary(self):
        self.assertEqual(local_time("2026-10-01T02:00:00Z"), pd.Timestamp("2026-09-30 23:00:00"))

    def test_brazilian_money_and_annual_proxy(self):
        self.assertEqual(cents("R$ 239,90"), 23990)
        m = independent_metrics("cliente_sintetico", self.raw([]))
        self.assertAlmostEqual(m["receita_liquida_mensal_equivalente_proxy"], 239.9 / 12 * .85)

    def test_missing_recency_is_not_imputed_in_stored_metrics(self):
        m = independent_metrics("cliente_sintetico", self.raw([]))
        self.assertTrue(np.isnan(m["recencia_dias"]))
        self.assertTrue(np.isnan(m["proporcao_video_90d"]))
        self.assertEqual(m["tendencia_incompleta"], 1)
        self.assertEqual(m["dias_ativos_90d"], 0)

    def test_watch_copy_removed_after_timezone_correction(self):
        rows = [
            ["cliente_sintetico", "garmin", "2026-09-30 15:00:00", "forca", 30],
            ["cliente_sintetico", "app", "2026-09-30 12:03:00", "forca", 30],
            ["cliente_sintetico", "app", "2026-09-29 12:00:00", "strength", 45],
            ["cliente_sintetico", "app", "2026-09-28 12:00:00", "run", 0],
        ]
        m = independent_metrics("cliente_sintetico", self.raw(rows))
        self.assertEqual(m["dias_ativos_90d"], 2)
        self.assertEqual(m["min_por_treino_90d"], 37.5)
        self.assertEqual(m["proporcao_video_90d"], 1)
        self.assertEqual(m["recencia_dias"], .5)
        self.assertEqual(m["variacao_treinos_30d"], 2)

    def test_tolerance_does_not_hide_structural_missingness(self):
        self.assertTrue(agrees(np.nan, np.nan))
        self.assertFalse(agrees(np.nan, 273, 1))
        self.assertTrue(agrees(98, 97, 1))
        self.assertFalse(agrees(99, 97, 1))


if __name__ == "__main__":
    unittest.main()
