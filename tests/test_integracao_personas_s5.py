"""Integração não pode perder pessoas, trocar rótulos ou inventar decisões."""
import json
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from complementar_entregas_personas_s5 import coherence, integrate


class IntegracaoPersonasTests(unittest.TestCase):
    def frames(self):
        value = pd.DataFrame({"user_id": ["sintetico_b", "sintetico_a"],
            "cluster": [pd.NA, pd.NA], "uplift": [.05, pd.NA],
            "acao_recomendada": ["pendente", "pendente"], "valor": [20, 30]})
        segments = pd.DataFrame({"user_id": ["sintetico_a", "sintetico_b"], "segmento": [0, 3]})
        return value, segments

    def test_bijective_merge_preserves_values_effects_and_decisions(self):
        value, segments = self.frames()
        out = integrate(value, segments)
        self.assertEqual(out.cluster.tolist(), [3, 0])
        self.assertEqual(out.persona.tolist(), ["Novatos", "Adormecidos"])
        pd.testing.assert_series_equal(out.uplift, value.uplift)
        pd.testing.assert_series_equal(out.acao_recomendada, value.acao_recomendada)
        self.assertEqual(out.valor.sum(), value.valor.sum())
        self.assertTrue(value.cluster.isna().all())

    def test_missing_person_cannot_silently_disappear(self):
        value, segments = self.frames()
        with self.assertRaisesRegex(ValueError, "Cobertura"):
            integrate(value, segments.iloc[:1])

    def test_duplicate_key_cannot_multiply_financial_value(self):
        value, segments = self.frames()
        with self.assertRaisesRegex(ValueError, "duplicada"):
            integrate(value, pd.concat([segments, segments.iloc[:1]]))

    def test_unknown_label_is_not_assigned_a_persona(self):
        value, segments = self.frames()
        segments.loc[0, "segmento"] = 4
        with self.assertRaisesRegex(ValueError, "desconhecido"):
            integrate(value, segments)

    def test_existing_conflicting_label_is_not_overwritten(self):
        value, segments = self.frames()
        value.loc[0, "cluster"] = 0
        with self.assertRaisesRegex(ValueError, "conflita"):
            integrate(value, segments)

    def profiles(self):
        return pd.DataFrame({"user_id": list("abcdef"), "segmento": [0, 1, 2, 2, 2, 3],
            "dias_ativos_90d": [2, 24, 26, 26, 26, 14],
            "proporcao_video_90d": [.17, .86, .19, .19, .19, .27],
            "min_por_treino_90d": [46, 41, 48, 48, 48, 43],
            "tempo_assinatura_dias": [338, 334, 361, 361, 361, 38],
            "taxa_dias_ativos_90d": [.02, .27, .30, .30, .30, .32],
            "seguidores_corte": [2, 2, 2, 2, 2, 0]})

    def test_coherence_evidence_is_json_serializable(self):
        _, checks = coherence(self.profiles())
        self.assertEqual(len(checks), 4)
        self.assertTrue(all(json.loads(json.dumps(checks)).values()))

    def test_changed_profile_requires_reassessment_of_names(self):
        profiles = self.profiles()
        profiles.loc[profiles.segmento.eq(1), "proporcao_video_90d"] = .1
        with self.assertRaisesRegex(ValueError, "não sustenta"):
            coherence(profiles)


if __name__ == "__main__":
    unittest.main()
