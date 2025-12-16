"""
build_index.py

Builds embeddings for SHL assessment catalog and
creates a FAISS index for semantic retrieval.

This is a ONE-TIME offline step.
"""

import os
import pickle
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# -------- Paths --------
CATALOG_PATH = "data/shl_catalog.csv"
INDEX_PATH = "models/faiss.index"
META_PATH = "models/metadata.pkl"

# -------- Model --------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    print("Loading SHL catalog...")
    df = pd.read_csv(CATALOG_PATH)

    if df.empty:
        raise ValueError("Catalog CSV is empty")

    print(f"Loaded {len(df)} assessments")

    # Create text to embed (simple & effective)
    texts = [
        f"{row['name']} assessment"
        for _, row in df.iterrows()
    ]

    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # important for cosine similarity
    )

    dimension = embeddings.shape[1]
    print(f"Embedding dimension: {dimension}")

    # Build FAISS index (exact search, simple & reliable)
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"FAISS index built with {index.ntotal} vectors")

    # Ensure output directory exists
    os.makedirs("models", exist_ok=True)

    # Save FAISS index
    faiss.write_index(index, INDEX_PATH)

    # Save metadata (id -> assessment info)
    metadata = df.to_dict(orient="records")
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("Index and metadata saved successfully")
    print(f"- FAISS index: {INDEX_PATH}")
    print(f"- Metadata: {META_PATH}")


if __name__ == "__main__":
    main()
