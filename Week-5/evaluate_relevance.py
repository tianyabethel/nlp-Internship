
import csv
import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

QUERIES = [
    "a family home with a large backyard",
    "a renovated kitchen with an open floor plan",
    "a quiet property with ocean views",
    "a home with a swimming pool",
    "a spacious property with mountain views",
    "a modern kitchen",
    "a house with a covered patio",
    "a property with a large lot",
    "a home near the beach",
    "a house with multiple bedrooms",
    "a home with a fireplace",
    "a property with a garden",
    "a home with a garage",
    "a recently remodeled house",
    "a home with hardwood floors",
    "a property with a guest house",
    "a home with a city view",
    "a house with an outdoor entertaining area",
    "a home with a spacious living room",
    "a property with mature trees",
    "a house with updated bathrooms",
    "a home with a breakfast nook",
    "a property on a quiet cul-de-sac",
    "a home with an open concept design",
    "a house with a large driveway",
    "a home with a new roof",
    "a property with an in-ground pool",
    "a home with a balcony",
    "a house with a walk-in closet",
    "a property with acreage",
    "a home with energy-efficient features",
    "a house with a guest suite",
    "a home with stainless steel appliances",
    "a property with a waterfront view",
    "a home with a fenced backyard",
    "a house with a single-level floor plan",
    "a property with room for entertaining",
    "a home with an updated interior",
    "a house with a home office",
    "a property with a patio and landscaping",
    "a home with vaulted ceilings",
    "a house with a laundry room",
    "a property with a mountain view",
    "a home with a spacious kitchen",
    "a house with a finished basement",
    "a property with a detached garage",
    "a home with a pool and spa",
    "a house with a formal dining room",
    "a property with a scenic view",
    "a home with an updated floor plan",
]

with open(ARTIFACTS / "properties.json", encoding="utf-8") as f:
    properties = json.load(f)

index = faiss.read_index(str(ARTIFACTS / "properties.faiss"))
model = SentenceTransformer("all-MiniLM-L6-v2")

output = ROOT / "relevance_judgments.csv"

with open(output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "query", "rank", "listing_id",
        "semantic_score", "remarks", "relevance_0_2"
    ])

    for query in QUERIES:
        vector = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")

        scores, ids = index.search(vector, 1)
        idx = int(ids[0][0])
        item = properties[idx]

        writer.writerow([
            query,
            1,
            item["listing_id"],
            round(float(scores[0][0]), 4),
            item["remarks"].replace("\n", " ")[:500],
            "",
        ])

print(f"Created {len(QUERIES)} query-result pairs.")
print(f"Saved evaluation CSV: {output}")
print("Label relevance as 0 (not relevant), 1 (partial), or 2 (highly relevant).")
