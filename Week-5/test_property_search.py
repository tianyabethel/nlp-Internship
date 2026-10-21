import json
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

print("Loading saved index and property data...")
index = faiss.read_index(str(ARTIFACTS / "properties.faiss"))

with open(ARTIFACTS / "properties.json", encoding="utf-8") as file:
    properties = json.load(file)

model = SentenceTransformer("all-MiniLM-L6-v2")

print(f"Loaded {index.ntotal:,} listings.")
print(f"Embedding dimensions: {index.d}")
print(f"Metadata records: {len(properties):,}")

queries = [
    "a family home with a large backyard",
    "a renovated kitchen with an open floor plan",
    "a quiet property with ocean views",
]

for query in queries:
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    start = time.perf_counter()
    scores, indices = index.search(query_embedding, 5)
    search_ms = (time.perf_counter() - start) * 1000

    print(f"\nQuery: {query}")
    print(f"FAISS retrieval latency: {search_ms:.2f} ms")

    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            item = properties[idx]
            print(
                f"  Score: {score:.3f} | "
                f"Listing: {item['listing_id']} | "
                f"{item['remarks'][:250]}"
            )
