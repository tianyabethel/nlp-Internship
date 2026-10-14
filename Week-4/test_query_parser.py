import unittest
from query_parser import QueryParser


class TestQueryParser(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_price_bedrooms_city(self):
        result = self.parser.parse("3 bed under 700k in Irvine")
        self.assertEqual(result["bedrooms"], 3)
        self.assertEqual(result["price_max"], 700000)
        self.assertEqual(result["city"], "irvine")

    def test_price_in_millions(self):
        result = self.parser.parse("under $1.2m")
        self.assertEqual(result["price_max"], 1200000)

    def test_minimum_price(self):
        result = self.parser.parse("over 400k")
        self.assertEqual(result["price_min"], 400000)

    def test_bathrooms(self):
        result = self.parser.parse("2 bath")
        self.assertEqual(result["bathrooms"], 2)

    def test_pool(self):
        result = self.parser.parse("house with pool")
        self.assertIn("pool", result["amenities"])

    def test_without_pool(self):
        result = self.parser.parse("house without pool")
        self.assertIn("pool", result["amenities_not"])
        self.assertNotIn("amenities", result)

    def test_safe_sql_parameters(self):
        sql, params = self.parser.to_sql({
            "price_max": 700000,
            "bedrooms": 3
        })
        self.assertIn("%s", sql)
        self.assertNotIn("700000", sql)
        self.assertEqual(params, [700000, 3])
    def test_invalid_city(self):
        self.assertTrue(self.parser.validate({"city": "Fakeville"}))

    def test_price_out_of_range(self):
        self.assertTrue(self.parser.validate({"price_max": 200000000}))

    def test_negative_price(self):
        self.assertTrue(self.parser.validate({"price_min": -100}))

    def test_bedrooms_out_of_range(self):
        self.assertTrue(self.parser.validate({"bedrooms": 25}))

    def test_min_price_greater_than_max(self):
        self.assertTrue(
            self.parser.validate({"price_min": 800000, "price_max": 500000})
        )

    def test_sql_injection_blocked(self):
        malicious = {"city": "Irvine' OR 1=1 --"}
        with self.assertRaises(ValueError):
            self.parser.to_sql(malicious)

    def test_sql_uses_parameters(self):
        sql, params = self.parser.to_sql({"price_max": 700000})
        self.assertIn("%s", sql)
        self.assertEqual(params, [700000])
        self.assertNotIn("700000", sql)

    def test_between_prices(self):
        result = self.parser.parse("between 400k and 700k")
        self.assertEqual(result["price_min"], 400000)
        self.assertEqual(result["price_max"], 700000)

    def test_garage_amenity(self):
        result = self.parser.parse("house with garage")
        self.assertIn("garage", result["amenities"])

    def test_no_garden(self):
        result = self.parser.parse("house with no garden")
        self.assertIn("garden", result["amenities_not"])

if __name__ == "__main__":
    unittest.main()
