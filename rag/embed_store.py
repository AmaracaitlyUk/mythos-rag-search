"""
Vector store: turn chunks into vectors and support similarity search over them.

Checkpoint 2 upgrade: real sentence embeddings instead of TF-IDF. Chunks are
encoded with a local sentence-transformers model (no API key, runs on CPU) into
dense semantic vectors, so retrieval now captures meaning rather than just
literal word/character overlap — e.g. a query about "the sea god" can match a
chunk about "Poseidon" even though they share no words in common, which pure
TF-IDF (word- or character-level) cannot do.

The VectorStore interface (`build`, `query`) is unchanged from the TF-IDF
version, so app.py and generate.py do not need to change at all.
"""

from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from .ingest import Chunk

# all-MiniLM-L6-v2: small, fast, runs well on CPU, strong default choice for
# semantic search at this scale. Downloads once (~90MB) and is cached locally
# afterward, so only the very first run is slow.
MODEL_NAME = "all-MiniLM-L6-v2"


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.embeddings = None  # shape: (n_chunks, embedding_dim), L2-normalized
        self.chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk]) -> None:
        """Encode all chunk text into normalized embedding vectors."""
        self.chunks = chunks
        texts = [c.text for c in chunks]
        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # so cosine similarity == dot product
            show_progress_bar=False,
        )

    def query(self, query_text: str, top_k: int = 3) -> List[Tuple[Chunk, float]]:
        """Return the top_k (chunk, similarity_score) pairs for a query string."""
        if self.embeddings is None:
            raise RuntimeError("VectorStore.build() must be called before query().")
        query_vec = self.model.encode(
            [query_text], normalize_embeddings=True, show_progress_bar=False
        )[0]
        # embeddings are L2-normalized, so dot product == cosine similarity
        scores = self.embeddings @ query_vec
        ranked_idx = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in ranked_idx]