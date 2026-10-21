import json
import re
import time
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

with open(ARTIFACTS / "properties.json", encoding="utf-8") as file:
    properties = json.load(file)

remarks = [item["remarks"] for item in properties]
index = faiss.read_index(str(ARTIFACTS / "properties.faiss"))
model = SentenceTransformer("all-MiniLM-L6-v2")

def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())

print("Building BM25 index...")
bm25 = BM25Okapi([tokenize(text) for text in remarks])

queries = [
    "a family home with a large backyard",
    "a renovated kitchen with an open floor plan",
    "a quiet property with ocean views",
]

for query in queries:
    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    start = time.perf_counter()
    semantic_scores, semantic_ids = index.search(query_vector, 5)
    semantic_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    keyword_scores = bm25.get_scores(tokenize(query))
    keyword_ids = np.argsort(keyword_scores)[::-1][:5]
    bm25_ms = (time.perf_counter() - start) * 1000

    print(f"\nQuery: {query}")
    print(f"FAISS retrieval: {semantic_ms:.2f} ms")
    print(f"BM25 retrieval:  {bm25_ms:.2f} ms")

    for label, ids in [
        ("Semantic", semantic_ids[0]),
        ("BM25", keyword_ids),
    ]:
        print(f"\n{label} top 3:")
        for idx in ids[:3]:
            print(f"  {properties[int(idx)]['listing_id']} | "
                  f"{properties[int(idx)]['remarks'][:180]}")

print("\nNote: Timings exclude query embedding and BM25 index construction.")
