import json
import os
from pathlib import Path

import faiss
import mysql.connector
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "Week-5" / "artifacts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / "backend" / ".env")

def main():
    print("Connecting to MySQL...")

    connection = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT L_ListingID, L_Remarks
            FROM rets_property
            WHERE L_Remarks IS NOT NULL
              AND TRIM(L_Remarks) <> ''
        """)
        rows = cursor.fetchall()
        cursor.close()
    finally:
        connection.close()

    if not rows:
        raise RuntimeError("No property remarks were found.")

    remarks = [str(row["L_Remarks"]).strip() for row in rows]
    print(f"Loaded {len(remarks):,} property remarks.")

    cache_path = OUTPUT_DIR / "property_embeddings.npy"

    if cache_path.exists():
        embeddings = np.load(cache_path)
        if len(embeddings) != len(remarks):
            raise RuntimeError("Embedding cache does not match the current database rows.")
        print(f"Loaded {len(embeddings):,} cached embeddings.")
    else:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding_parts = []

        for start in range(0, len(remarks), 128):
            batch = remarks[start:start + 128]
            batch_embeddings = model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            embedding_parts.append(batch_embeddings.astype("float32"))
            print(f"Encoded {min(start + len(batch), len(remarks)):,}/{len(remarks):,}")

        embeddings = np.vstack(embedding_parts)
        np.save(cache_path, embeddings)
        print("Saved embedding cache.")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(OUTPUT_DIR / "properties.faiss"))

    metadata = [
        {"listing_id": str(row["L_ListingID"]), "remarks": remark}
        for row, remark in zip(rows, remarks)
    ]
    with open(OUTPUT_DIR / "properties.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)

    print(f"Saved FAISS index with {index.ntotal:,} listings.")
    print(f"Embedding dimensions: {embeddings.shape[1]}")
    print(f"Artifacts saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
