import os
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "models/faiss.index"
META_PATH = "models/metadata.pkl"
CATALOG_PATH = "data/shl_catalog.csv"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SHLRecommender:
    def __init__(self, top_k=10):
        self.top_k = top_k
        self.model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")

        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self._load_index()
        else:
            self._build_index()

    def _build_index(self):
        print("Building FAISS index from catalog...")

        df = pd.read_csv(CATALOG_PATH)
        texts = df["name"].tolist()

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        self.metadata = df.to_dict(orient="records")

        os.makedirs("models", exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

        import pickle
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

        print("FAISS index built successfully")

    def _load_index(self):
        print("Loading FAISS index from disk...")
        self.index = faiss.read_index(INDEX_PATH)

        import pickle
        with open(META_PATH, "rb") as f:
            self.metadata = pickle.load(f)

    def recommend(self, query: str):
        query_emb = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        _, indices = self.index.search(query_emb, self.top_k)

        results = []
        for idx in indices[0]:
            item = self.metadata[idx]
            results.append({
                "assessment_name": item["name"],
                "assessment_url": item["url"]
            })

        return results
