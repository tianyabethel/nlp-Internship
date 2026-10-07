import sys
import pandas as pd

sys.path.insert(0, "Week-3/scripts")

from entity_extractor import EntityExtractor


input_file = "Week-2/data/processed/listing_sample_cleaned.csv"
output_file = "Week-3/data/processed/listing_entities.csv"

df = pd.read_csv(input_file)

extractor = EntityExtractor()

df["entities"] = df["cleaned_remarks"].fillna("").apply(
    extractor.extract_all
)

df.to_csv(output_file, index=False)

print(f"Extracted entities from {len(df)} listings.")
print(f"Saved to: {output_file}")