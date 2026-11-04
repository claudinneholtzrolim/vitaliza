import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from valor_priorizacao_s5 import contribution, incremental_value, max_offers


class FinancialPolicyTests(unittest.TestCase):
    def test_store_monthly_margin_matches_contract(self):
        self.assertAlmostEqual(contribution(39.9, "mensal", "app_store"), 29.715)

    def test_promotional_annual_is_not_full_renewal_price(self):
        promotional = contribution(239.9, "anual", "google_play")
        full = contribution(299.9, "anual", "google_play")
        self.assertAlmostEqual((full-promotional)*12, 51)

    def test_zero_or_negative_effect_still_costs_money(self):
        self.assertAlmostEqual(incremental_value(0, 3, 30, .01, 35.91), -35.92)
        self.assertLess(incremental_value(-.05, 3, 30, 0), 0)

    def test_paid_period_does_not_create_extra_value(self):
        self.assertEqual(incremental_value(.8, 0, 30, 18), -18)

    def test_budget_never_overspends_decimal_boundary(self):
        self.assertEqual(max_offers(35.91,0,0,35.91),1)
        self.assertEqual(max_offers(40000,6147.53,1000,35.91),914)
        self.assertEqual(max_offers(1,2,0,25),0)

    def test_invalid_cost_and_probability_rejected(self):
        with self.assertRaises(ValueError): incremental_value(1.01,3,30,.4)
        with self.assertRaises(ValueError): max_offers(40000,0,0,0)


if __name__ == "__main__":
    unittest.main()
