import pandas as pd

input_file = "Week-2/data/processed/listing_sample_cleaned.csv"
output_file = "Week-3/data/processed/labeled_entities.csv"

df = pd.read_csv(input_file)

# Use 250 remarks for the labeled dataset
labeled = df.head(250).copy()

def find_span(text, value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    start = text.lower().find(value.lower())

    if start == -1:
        return None

    return {
        "text": text[start:start + len(value)],
        "start": start,
        "end": start + len(value)
    }


def create_labels(row):
    text = row["cleaned_remarks"]

    labels = []

    bedroom = find_span(text, row["beds"])
    if bedroom:
        labels.append({
            "entity": "BEDROOM",
            **bedroom
        })

    bathroom = find_span(text, row["baths"])
    if bathroom:
        labels.append({
            "entity": "BATHROOM",
            **bathroom
        })

    price = find_span(text, row["price"])
    if price:
        labels.append({
            "entity": "PRICE",
            **price
        })

    return labels


labeled["entity_spans"] = labeled.apply(create_labels, axis=1)

labeled.to_csv(output_file, index=False)

print(f"Created labeled dataset with {len(labeled)} remarks.")
print(f"Saved to: {output_file}")
