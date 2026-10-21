import json
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

with open(ARTIFACTS / "properties.json", encoding="utf-8") as file:
    properties = json.load(file)

embeddings = np.load(ARTIFACTS / "property_embeddings.npy")
count = min(10_000, len(properties))

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(np.ascontiguousarray(embeddings[:count], dtype="float32"))

model = SentenceTransformer("all-MiniLM-L6-v2")
queries = [
    "a family home with a large backyard",
    "a renovated kitchen with an open floor plan",
    "a quiet property with ocean views",
    "a home with a swimming pool",
    "a spacious property with mountain views",
]

# Warm up model and index before measuring.
model.encode([queries[0]], normalize_embeddings=True)
index.search(embeddings[:1], 5)

embedding_times = []
retrieval_times = []
total_times = []

for query in queries:
    start = time.perf_counter()
    vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")
    embedding_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    index.search(vector, 5)
    retrieval_ms = (time.perf_counter() - start) * 1000

    embedding_times.append(embedding_ms)
    retrieval_times.append(retrieval_ms)
    total_times.append(embedding_ms + retrieval_ms)

print(f"Benchmark index size: {index.ntotal:,} listings")
print(f"Mean query-embedding time: {np.mean(embedding_times):.2f} ms")
print(f"Mean FAISS retrieval time: {np.mean(retrieval_times):.2f} ms")
print(f"Mean end-to-end search time: {np.mean(total_times):.2f} ms")
print(f"Maximum end-to-end search time: {max(total_times):.2f} ms")
print(f"Target under 100 ms: {'PASS' if max(total_times) < 100 else 'NOT MET'}")
