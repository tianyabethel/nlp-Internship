import json
import pandas as pd


def test_taxonomy_loaded():
    with open("Week-1/data/processed/taxonomy.json", "r") as f:
        taxonomy = json.load(f)

    terms = [
        term
        for category in taxonomy.values()
        for term in category
    ]

    assert len(taxonomy) == 8
    assert len(terms) >= 200


def test_sample_data_quality():
    df = pd.read_csv("Week-1/data/processed/listing_sample.csv")

    assert len(df) >= 500
    assert df["remarks"].notna().all()
    assert (df["remarks"].str.len() > 50).all()


def test_taxonomy_coverage():
    with open("Week-1/data/processed/taxonomy.json", "r") as f:
        taxonomy = json.load(f)

    terms = [
        term.lower()
        for category in taxonomy.values()
        for term in category
    ]

    df = pd.read_csv("Week-1/data/processed/listing_sample.csv")

    matched = 0

    for remark in df["remarks"].fillna("").astype(str).str.lower():
        if any(term in remark for term in terms):
            matched += 1

    coverage = matched / len(df)

    print(f"\nTaxonomy coverage: {coverage:.2%}")

    assert coverage >= 0.30
