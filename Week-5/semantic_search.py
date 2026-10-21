import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


class SemanticSearcher:
    """Semantic property search using sentence-transformers and FAISS."""

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.listings = []
        self.remarks = []
        self.build_seconds = 0.0

    def build_index(self, remarks_list, listings=None):
        """Encode listing remarks and build a cosine-similarity FAISS index."""
        cleaned = [
            str(text).strip() if text is not None else ""
            for text in remarks_list
        ]

        if not cleaned or not any(cleaned):
            raise ValueError("At least one non-empty listing remark is required.")

        self.remarks = cleaned
        self.listings = listings if listings is not None else cleaned

        start = time.perf_counter()
        embeddings = self.model.encode(
            cleaned,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype("float32")

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.build_seconds = time.perf_counter() - start

        print(f"Indexed {len(cleaned):,} listings.")
        print(f"Embedding dimensions: {embeddings.shape[1]}")
        print(f"Index build time: {self.build_seconds:.2f} seconds")

    def search(self, query, top_k=10):
        """Return the top matching listings and similarity scores."""
        if self.index is None:
            raise RuntimeError("Call build_index() before search().")
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.remarks)),
        )

        return [
            {
                "listing": self.listings[int(i)],
                "remarks": self.remarks[int(i)],
                "score": float(score),
            }
            for score, i in zip(scores[0], indices[0])
            if i >= 0
        ]


class BM25Searcher:
    """Keyword-based ranking for comparison with semantic search."""

    def __init__(self, remarks_list, listings=None):
        self.remarks = [str(text or "") for text in remarks_list]
        self.listings = listings if listings is not None else self.remarks
        tokenized = [text.lower().split() for text in self.remarks]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query, top_k=10):
        scores = self.bm25.get_scores(query.lower().split())
        indices = np.argsort(scores)[::-1][:top_k]

        return [
            {
                "listing": self.listings[int(i)],
                "remarks": self.remarks[int(i)],
                "score": float(scores[i]),
            }
            for i in indices
        ]


def compare_searchers(semantic, bm25, queries, top_k=5):
    """Report average retrieval latency for both search methods."""
    for name, searcher in [("Semantic", semantic), ("BM25", bm25)]:
        durations = []

        for query in queries:
            start = time.perf_counter()
            searcher.search(query, top_k=top_k)
            durations.append((time.perf_counter() - start) * 1000)

        print(
            f"{name}: average search latency "
            f"{np.mean(durations):.2f} ms across {len(queries)} queries"
        )


if __name__ == "__main__":
    # Small smoke test; replace with real listing remarks for project evaluation.
    sample_remarks = [
        "Spacious family home with a large backyard and patio.",
        "Modern downtown apartment near restaurants and public transit.",
        "Quiet countryside property with acreage and mountain views.",
        "Renovated kitchen, open floor plan, and room for entertaining.",
    ]

    searcher = SemanticSearcher()
    searcher.build_index(sample_remarks)

    keyword_searcher = BM25Searcher(sample_remarks)
    query = "home with outdoor space for family gatherings"

    print("\nSemantic search results:")
    for result in searcher.search(query, top_k=3):
        print(f"{result['score']:.3f} | {result['remarks']}")

    print("\nBM25 search results:")
    for result in keyword_searcher.search(query, top_k=3):
        print(f"{result['score']:.3f} | {result['remarks']}")
