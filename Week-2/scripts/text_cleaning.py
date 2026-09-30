
import re
import html
import unicodedata


class TextCleaner:

    def __init__(self):
        self.abbrev_map = {
            "br": "bedroom",
            "brs": "bedrooms",
            "ba": "bathroom",
            "bas": "bathrooms",
            "bdrm": "bedroom",
            "bdrms": "bedrooms",
            "bd": "bedroom",
            "bds": "bedrooms",
            "sqft": "square feet",
            "sq ft": "square feet",
            "sf": "square feet",
            "w/": "with",
            "w/o": "without",
            "mbr": "master bedroom",
            "fp": "fireplace",
            "frpl": "fireplace",
            "gar": "garage",
            "a/c": "air conditioning",
            "hvac": "heating and air conditioning",
            "kit": "kitchen",
            "kitch": "kitchen",
            "lr": "living room",
            "liv rm": "living room",
            "dr": "dining room",
            "din rm": "dining room",
            "fam rm": "family room",
            "w/d": "washer and dryer",
            "hoa": "homeowners association",
            "pvt": "private",
            "remod": "remodeled",
            "renov": "renovated",
            "upd": "updated",
            "ss": "stainless steel",
            "yr": "year",
            "yrs": "years",
        }

    def normalize_unicode(self, text):
        """Standardize unicode characters."""
        if not isinstance(text, str):
            return ""

        text = unicodedata.normalize("NFKC", text)

        text = text.replace("’", "'")
        text = text.replace("“", '"')
        text = text.replace("”", '"')
        text = text.replace("–", "-")
        text = text.replace("—", "-")
        text = text.replace("\u00a0", " ")

        return text

    def normalize_html(self, text):
        """Remove HTML tags and decode HTML entities."""
        if not isinstance(text, str):
            return ""

        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)

        return text

    def normalize_prices(self, text):
        """Convert 450k to 450000 and 1.2m to 1200000."""
        if not isinstance(text, str):
            return ""

        def convert_price(match):
            number = float(match.group(1))
            unit = match.group(2).lower()

            if unit == "k":
                number *= 1000
            elif unit == "m":
                number *= 1000000

            return str(int(number))

        return re.sub(
            r"(\d+(?:\.\d+)?)\s*([km])\b",
            convert_price,
            text,
            flags=re.IGNORECASE
        )

    def normalize_measurements(self, text):
        """Convert 2,000 sqft to 2000 square feet."""
        if not isinstance(text, str):
            return ""

        def convert_measurement(match):
            number = match.group(1).replace(",", "")
            return f"{number} square feet"

        return re.sub(
     r"(\d[\d,]*)\s*(sqft|sq\s*\.?\s*ft\.?|sf)\.?",
            convert_measurement,
            text,
            flags=re.IGNORECASE
        )

    def expand_abbreviations(self, text):
        """Expand common real-estate abbreviations."""
        if not isinstance(text, str):
            return ""

        for abbreviation, replacement in self.abbrev_map.items():
            pattern = r"(?<!\w)" + re.escape(abbreviation) + r"(?!\w)"

            text = re.sub(
                pattern,
                replacement,
                text,
                flags=re.IGNORECASE
            )

        return text

    def normalize_whitespace(self, text):
        """Remove extra spaces and line breaks."""
        if not isinstance(text, str):
            return ""

        return re.sub(r"\s+", " ", text).strip()

    def clean_text(self, text):
        """Run the complete cleaning pipeline."""
        text = self.normalize_unicode(text)
        text = self.normalize_html(text)
        text = self.normalize_prices(text)
        text = self.normalize_measurements(text)
        text = self.expand_abbreviations(text)
        text = self.normalize_whitespace(text)

        return text
    def profile_column(self, df, column_name):
        """Analyze what needs cleaning in a text column."""

        column = df[column_name]

        return {
            "null_rate": column.isnull().mean(),
            "avg_length": column.dropna().str.len().mean(),
            "common_terms": self._extract_top_terms(column),
            "price_mentions": column.fillna("").str.contains(
                r"\$\d|\d+(?:\.\d+)?[km]\b",
                case=False,
                regex=True
            ).sum(),
            "has_html": column.fillna("").str.contains(
                r"<[^>]+>",
                regex=True
            ).sum(),
            "common_abbreviations": self._detect_abbreviations(column)
        }

    def _extract_top_terms(self, column):
        """Find the most common words."""
        words = []

        for text in column.dropna():
            words.extend(
                re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
            )

        from collections import Counter

        return Counter(words).most_common(10)

    def _detect_abbreviations(self, column):
        """Find abbreviations from the abbreviation dictionary."""
        results = {}

        for abbreviation in self.abbrev_map:
            pattern = r"(?<!\w)" + re.escape(abbreviation) + r"(?!\w)"

            count = column.fillna("").str.contains(
                pattern,
                case=False,
                regex=True
            ).sum()

            if count > 0:
                results[abbreviation] = int(count)

        return results
if __name__ == "__main__":
    import pandas as pd
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]

    input_file = root / "Week-1/data/processed/listing_sample.csv"
    output_file = root / "Week-2/data/processed/listing_sample_cleaned.csv"
    report_file = root / "Week-2/reports/data_profile.json"

    df = pd.read_csv(input_file)

    cleaner = TextCleaner()

    # Create cleaned remarks
    df["cleaned_remarks"] = df["remarks"].apply(
        cleaner.clean_text
    )

    # Save cleaned dataset
    df.to_csv(output_file, index=False)

    # Create profiling report
    profile = cleaner.profile_column(df, "remarks")

    with open(report_file, "w") as f:
        json.dump(profile, f, indent=2, default=int)

    print("Cleaned dataset created:")
    print(output_file)

    print("Data profile created:")
    print(report_file)