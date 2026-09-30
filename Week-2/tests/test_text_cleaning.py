import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts")
)

from text_cleaning import TextCleaner


@pytest.fixture
def cleaner():
    return TextCleaner()


# Unicode tests
@pytest.mark.parametrize("text, expected", [
    ("beautiful \u201chome\u201d", 'beautiful "home"'),
    ("owner\u2019s home", "owner's home"),
    ("large \u2014 spacious", "large - spacious"),
    ("hello\u00a0world", "hello world"),
    ("café", "café"),
])
def test_unicode(cleaner, text, expected):
    assert cleaner.normalize_unicode(text) == expected


# HTML tests
@pytest.mark.parametrize("text, expected", [
    ("<p>Beautiful home</p>", " Beautiful home "),
    ("<b>Luxury</b> home", " Luxury  home"),
    ("Home &amp; garden", "Home & garden"),
    ("<div>Great property</div>", " Great property "),
    ("No HTML here", "No HTML here"),
])
def test_html(cleaner, text, expected):
    assert cleaner.normalize_html(text) == expected


# Price tests
@pytest.mark.parametrize("text, expected", [
    ("450k", "450000"),
    ("450K", "450000"),
    ("1.2m", "1200000"),
    ("1.2M", "1200000"),
    ("750k home", "750000 home"),
    ("$450k", "$450000"),
    ("$1.2m", "$1200000"),
])
def test_prices(cleaner, text, expected):
    assert cleaner.normalize_prices(text) == expected


# Measurement tests
@pytest.mark.parametrize("text, expected", [
    ("2,000 sqft", "2000 square feet"),
    ("2000 sqft", "2000 square feet"),
    ("2,000 sq ft", "2000 square feet"),
    ("2,000 sq. ft.", "2000 square feet"),
    ("1800 sf", "1800 square feet"),
    ("1,500 SF", "1500 square feet"),
])
def test_measurements(cleaner, text, expected):
    assert cleaner.normalize_measurements(text) == expected


# Abbreviation tests
@pytest.mark.parametrize("text, expected", [
    ("3 br", "3 bedroom"),
    ("4 brs", "4 bedrooms"),
    ("2 ba", "2 bathroom"),
    ("3 bas", "3 bathrooms"),
    ("master br", "master bedroom"),
    ("mbr suite", "master bedroom suite"),
    ("w/ pool", "with pool"),
    ("w/o HOA", "without homeowners association"),
    ("fp", "fireplace"),
    ("gar", "garage"),
    ("kit", "kitchen"),
    ("kitch", "kitchen"),
    ("lr", "living room"),
    ("dr", "dining room"),
    ("fam rm", "family room"),
    ("w/d", "washer and dryer"),
    ("pvt yard", "private yard"),
    ("remod home", "remodeled home"),
    ("renov home", "renovated home"),
    ("upd kitchen", "updated kitchen"),
])
def test_abbreviations(cleaner, text, expected):
    assert cleaner.expand_abbreviations(text) == expected


# Whitespace tests
@pytest.mark.parametrize("text, expected", [
    ("hello   world", "hello world"),
    ("hello\nworld", "hello world"),
    ("hello\tworld", "hello world"),
    ("  hello world  ", "hello world"),
    ("hello    beautiful    home", "hello beautiful home"),
])
def test_whitespace(cleaner, text, expected):
    assert cleaner.normalize_whitespace(text) == expected


# Full cleaning pipeline
@pytest.mark.parametrize("text, expected", [
    ("3 br, 2 ba", "3 bedroom, 2 bathroom"),
    ("450k home", "450000 home"),
    ("2,000 sqft home", "2000 square feet home"),
    ("<p>Beautiful 3 br home</p>", "Beautiful 3 bedroom home"),
    ("2 br w/ pool", "2 bedroom with pool"),
    ("$1.2m 4 br home", "$1200000 4 bedroom home"),
    ("  3 BR   2 BA  ", "3 bedroom 2 bathroom"),
])
def test_clean_text(cleaner, text, expected):
    assert cleaner.clean_text(text) == expected


# Null / non-string tests
def test_none(cleaner):
    assert cleaner.clean_text(None) == ""


def test_empty_string(cleaner):
    assert cleaner.clean_text("") == ""


# Profiling tests
def test_profiling(cleaner):
    df = pd.DataFrame({
        "remarks": [
            "3 br home w/ pool",
            "2 ba home",
            None,
            "<p>Beautiful home</p>",
            "450k property"
        ]
    })

    profile = cleaner.profile_column(df, "remarks")

    assert "null_rate" in profile
    assert "avg_length" in profile
    assert "common_terms" in profile
    assert "price_mentions" in profile
    assert "has_html" in profile
    assert "common_abbreviations" in profile


def test_abbreviation_dictionary_has_30_plus_entries(cleaner):
    assert len(cleaner.abbrev_map) >= 30