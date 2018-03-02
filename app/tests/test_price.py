import unittest
from decimal import Decimal

from app.mod_stats.stats_utils import StatsDataExtractor, PriceValue
from .config import DATA_DIR


class TestPrice(unittest.TestCase):
    """
    Checks PriceValue class and its methods
    """
    def setUp(self):
        self.gross_raw = 1.0
        self.tax_rate = 20
        self.gross_value = PriceValue(self.gross_raw).get_value()
        self.divider = PriceValue(1 + self.tax_rate / 100).get_value()
        self.raw_net_amount = PriceValue(self.gross_value / self.divider).round_half_up()
        self.vat = PriceValue(-1 * (self.raw_net_amount - self.gross_value)).round_half_up()
        self.net_amount = self.gross_value - self.vat

    def test_gross_value(self):
        self.assertEqual(self.gross_value, 1.0)

    def test_divider(self):
        self.assertEqual(self.divider, Decimal('1.20'))

    def test_raw_net_amount(self):
        self.assertEqual(self.raw_net_amount, Decimal('0.83'))

    def test_vat(self):
        self.assertEqual(self.vat, Decimal('0.17'))

    def test_net_amount(self):
        self.assertEqual(self.net_amount, Decimal('0.83'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
