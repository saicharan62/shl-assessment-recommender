"""
recommend.py

Semantic recommendation logic:
query text -> top K SHL assessments
"""

import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# -------- Paths --------
INDEX_PATH = "models/faiss.index"
META_PATH = "models/metadata.pkl"

# -------- Model --------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SHLRecommender:
    def __init__(self, top_k: int = 10):
        self.top_k = top_k

        print("Loading FAISS index...")
        self.index = faiss.read_index(INDEX_PATH)

        print("Loading metadata...")
        with open(META_PATH, "rb") as f:
            self.metadata = pickle.load(f)

        print("Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        if self.index.ntotal != len(self.metadata):
            raise ValueError("Index size and metadata size mismatch")

        print("Recommender ready")

    def recommend(self, query: str):
        """
        Returns top-K relevant assessments for a given query.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Embed query
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        # Search FAISS
        distances, indices = self.index.search(query_embedding, self.top_k)

        results = []
        for idx in indices[0]:
            item = self.metadata[idx]
            results.append({
                "assessment_name": item["name"],
                "assessment_url": item["url"]
            })

        return results


# -------- Manual test --------
if __name__ == "__main__":
    recommender = SHLRecommender(top_k=5)

    query = "Looking for a cognitive ability test for fresh graduates"
    results = recommender.recommend(query)

    print("\nRecommendations:")
    for r in results:
        print("-", r["name"], "→", r["url"])
