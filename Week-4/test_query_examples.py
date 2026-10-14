import unittest
from query_parser import QueryParser


class TestQueryExamples(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_price_examples(self):
        cases = [
            ("under 300k", 300000),
            ("under 450k", 450000),
            ("under 500k", 500000),
            ("under 600k", 600000),
            ("under 700k", 700000),
            ("under 800k", 800000),
            ("under 900k", 900000),
            ("under 1m", 1000000),
            ("under $1.2m", 1200000),
            ("below 650k", 650000),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                self.assertEqual(
                    self.parser.parse(query)["price_max"], expected
                )

    def test_minimum_price_examples(self):
        cases = [
            ("over 300k", 300000),
            ("over 400k", 400000),
            ("over 500k", 500000),
            ("over 600k", 600000),
            ("over 700k", 700000),
            ("above 450k", 450000),
            ("above 800k", 800000),
            ("over $1m", 1000000),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                self.assertEqual(
                    self.parser.parse(query)["price_min"], expected
                )

    def test_bedroom_examples(self):
        cases = [
            ("1 bed", 1),
            ("2 beds", 2),
            ("3 bedroom", 3),
            ("4 bedrooms", 4),
            ("5 br", 5),
            ("6 bed", 6),
            ("2+ bedrooms", 2),
            ("3 br house", 3),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                self.assertEqual(
                    self.parser.parse(query)["bedrooms"], expected
                )

    def test_bathroom_examples(self):
        cases = [
            ("1 bath", 1),
            ("2 baths", 2),
            ("3 bathroom", 3),
            ("4 bathrooms", 4),
            ("2 ba", 2),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                self.assertEqual(
                    self.parser.parse(query)["bathrooms"], expected
                )

    def test_amenity_examples(self):
        cases = [
            ("house with pool", "pool"),
            ("house with garage", "garage"),
            ("house with garden", "garden"),
            ("house with fireplace", "fireplace"),
        ]
        for query, amenity in cases:
            with self.subTest(query=query):
                self.assertIn(
                    amenity, self.parser.parse(query)["amenities"]
                )

    def test_negation_examples(self):
        cases = [
            ("house without pool", "pool"),
            ("house with no pool", "pool"),
            ("house without garage", "garage"),
            ("house with no garden", "garden"),
        ]
        for query, amenity in cases:
            with self.subTest(query=query):
                self.assertIn(
                    amenity, self.parser.parse(query)["amenities_not"]
                )
    def test_extra_price_examples(self):
        cases = [
            ("under 250k", 250000),
            ("under 350k", 350000),
            ("under 550k", 550000),
            ("under 750k", 750000),
            ("under 950k", 950000),
            ("below 400k", 400000),
            ("below 850k", 850000),
            ("above 350k", 350000),
            ("above 550k", 550000),
            ("above 750k", 750000),
            ("over 1.5m", 1500000),
            ("under $2m", 2000000),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                result = self.parser.parse(query)
                key = "price_min" if query.startswith(("above", "over")) else "price_max"
                self.assertEqual(result[key], expected)

if __name__ == "__main__":
    unittest.main()