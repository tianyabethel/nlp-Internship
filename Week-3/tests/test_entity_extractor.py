import sys

sys.path.insert(0, "Week-3/scripts")

from entity_extractor import EntityExtractor


def test_bedrooms():
    extractor = EntityExtractor()
    assert extractor.extract_bedrooms("This is a 4 bedroom home") == 4


def test_bathrooms():
    extractor = EntityExtractor()
    assert extractor.extract_bathrooms("This home has 2.5 bathrooms") == 2.5


def test_sqft():
    extractor = EntityExtractor()
    assert extractor.extract_sqft("This home has 2,000 square feet") == 2000


def test_amenities():
    extractor = EntityExtractor()
    result = extractor.extract_amenities(
        "Home with fireplace, pool, garage and balcony"
    )

    assert "fireplace" in result
    assert "pool" in result
    assert "garage" in result
    assert "balcony" in result


def test_extract_all():
    extractor = EntityExtractor()

    result = extractor.extract_all(
        "4 bedroom, 3 bathroom home with 2771 square feet, fireplace and pool"
    )

    assert result["bedrooms"] == 4
    assert result["bathrooms"] == 3.0
    assert result["sqft"] == 2771
    assert "fireplace" in result["amenities"]
    assert "pool" in result["amenities"]
