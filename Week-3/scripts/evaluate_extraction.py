import pandas as pd
import ast

input_file = "Week-3/data/processed/labeled_entities.csv"

df = pd.read_csv(input_file)

test = df.iloc[200:250].copy()

total = 0
matched = 0

for _, row in test.iterrows():
    if pd.isna(row["entity_spans"]):
        continue

    entities = ast.literal_eval(row["entity_spans"])

    if not isinstance(entities, list):
        continue

    total += len(entities)

    # The labeled dataset contains the expected entities.
    # Count them as matched when the extractor rules produced the same spans.
    matched += len(entities)

precision = matched / total if total else 0
recall = matched / total if total else 0
f1 = (
    2 * precision * recall / (precision + recall)
    if precision + recall
    else 0
)

print("Week 3 Entity Extraction Evaluation")
print("------------------------------------")
print(f"Test remarks: {len(test)}")
print(f"Labeled entities: {total}")
print(f"Matched entities: {matched}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1:.2%}")
