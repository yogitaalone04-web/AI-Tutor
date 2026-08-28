from typing import Dict, List, Any, Optional
import numpy as np
import faiss

class VectorStoreService:
    def __init__(self):
        # In-memory session store: session_id -> { "index": faiss.Index, "chunks": [...], "filename": str, "total_pages": int }
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session_index(
        self,
        session_id: str,
        embeddings: List[List[float]],
        chunks: List[Dict[str, Any]],
        filename: str,
        total_pages: int
    ) -> None:
        """
        Creates a FAISS index for a session using chunk embeddings.
        Normalizes embeddings to calculate cosine similarity via inner product.
        """
        if not embeddings or not chunks:
            raise ValueError("Embeddings and chunks cannot be empty.")

        embed_matrix = np.array(embeddings, dtype=np.float32)
        
        # Normalize vectors for Cosine Similarity (IndexFlatIP)
        faiss.normalize_L2(embed_matrix)
        
        dimension = embed_matrix.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embed_matrix)

        self._sessions[session_id] = {
            "index": index,
            "chunks": chunks,
            "filename": filename,
            "total_pages": total_pages
        }
        print(f"[VectorStoreService] Created {dimension}-dim FAISS index for session '{session_id}' with {len(chunks)} chunks across {total_pages} pages.")

    def search(self, session_id: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the FAISS index for the top-k most relevant chunks for a given query embedding.
        Returns a list of chunk metadata dicts with similarity scores.
        """
        session_data = self._sessions.get(session_id)
        if not session_data:
            raise KeyError(f"Session '{session_id}' not found. Please upload a textbook PDF first.")

        index: faiss.Index = session_data["index"]
        chunks: List[Dict[str, Any]] = session_data["chunks"]

        query_matrix = np.array([query_embedding], dtype=np.float32)
        if query_matrix.shape[1] != index.d:
            raise ValueError(f"Query embedding dimension ({query_matrix.shape[1]}) does not match FAISS index dimension ({index.d}).")

        faiss.normalize_L2(query_matrix)

        # Search index
        scores, indices = index.search(query_matrix, min(top_k, len(chunks)))

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1 and idx < len(chunks):
                chunk_data = dict(chunks[idx])
                chunk_data["score"] = float(score)
                results.append(chunk_data)

        return results

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_data = self._sessions.get(session_id)
        if not session_data:
            return None
        return {
            "filename": session_data["filename"],
            "total_pages": session_data["total_pages"],
            "total_chunks": len(session_data["chunks"])
        }

vectorstore_service = VectorStoreService()
