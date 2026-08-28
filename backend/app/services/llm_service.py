import os
import re
from typing import List, Dict, Any
import numpy as np
import google.generativeai as genai
from app.core.config import settings

class LLMService:
    def __init__(self):
        self._configured = False
        self._init_api()

    def _init_api(self):
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if api_key and api_key.startswith("AIzaSy"):
            try:
                genai.configure(api_key=api_key)
                self._configured = True
            except Exception as e:
                print(f"[LLMService] Gemini API init error: {e}")
                self._configured = False
        else:
            print("[LLMService] Note: Standard Gemini API key (AIzaSy...) not detected. Local fallback engine active.")
            self._configured = False

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates text embeddings using Gemini API (with local TF-IDF fallback if key is unauthenticated).
        """
        if self._configured:
            for model_name in [settings.EMBEDDING_MODEL, "models/gemini-embedding-001", "models/embedding-001"]:
                try:
                    embeddings: List[List[float]] = []
                    batch_size = 50
                    for i in range(0, len(texts), batch_size):
                        batch = texts[i:i + batch_size]
                        res = genai.embed_content(
                            model=model_name,
                            content=batch,
                            task_type="retrieval_document"
                        )
                        if "embedding" in res and isinstance(res["embedding"], list):
                            if len(res["embedding"]) > 0 and isinstance(res["embedding"][0], list):
                                embeddings.extend(res["embedding"])
                            else:
                                embeddings.append(res["embedding"])
                        elif isinstance(res, list):
                            embeddings.extend(res)

                    if len(embeddings) == len(texts):
                        return embeddings
                except Exception as e:
                    print(f"[LLMService] Embedding model '{model_name}' failed: {e}")
                    continue

        # Local Fallback Vector Generator (TF-IDF hash vector matching EMBEDDING_DIM)
        return [self._local_text_vector(t) for t in texts]

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generates embedding vector for a search query.
        """
        if self._configured:
            for model_name in [settings.EMBEDDING_MODEL, "models/gemini-embedding-001", "models/embedding-001"]:
                try:
                    res = genai.embed_content(
                        model=model_name,
                        content=query,
                        task_type="retrieval_query"
                    )
                    if "embedding" in res:
                        return res["embedding"]
                except Exception:
                    continue

        return self._local_text_vector(query)

    def generate_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Generates answer using Gemini LLM (with fallback to grounded textbook summary).
        """
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks):
            page_info = f"[Page {chunk['page']}]" if 'page' in chunk else ""
            context_blocks.append(f"--- EXCERPT {idx + 1} {page_info} ---\n{chunk['text']}")
        
        context_str = "\n\n".join(context_blocks)

        system_prompt = (
            "You are AI Tutor, a patient, encouraging academic tutor.\n"
            "Using ONLY the textbook excerpts provided below, answer the student's question clearly, thoroughly, and step-by-step.\n\n"
            "GUIDELINES:\n"
            "1. Format your response cleanly using Markdown (headers, bold text, bullet points, code blocks where appropriate).\n"
            "2. Cite the page numbers when referencing facts (e.g., '[Page 14]').\n"
            "3. If the provided textbook excerpts DO NOT contain the answer to the question, state honestly:\n"
            "   'I searched the uploaded textbook, but could not find information covering this specific question.'\n"
            "4. Do NOT invent information outside the provided textbook excerpts.\n\n"
            f"=== TEXTBOOK EXCERPTS ===\n{context_str}\n=========================\n\n"
            f"STUDENT QUESTION: {question}\n\n"
            "TUTOR ANSWER:"
        )

        if self._configured:
            for model_name in ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-pro"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(system_prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    print(f"[LLMService] Gemini model '{model_name}' call failed: {e}")
                    continue

        # Local Grounded Fallback Answer Generator
        return self._generate_local_grounded_answer(question, retrieved_chunks)

    def _local_text_vector(self, text: str, dim: int = None) -> List[float]:
        """
        Generates a normalized hash vector (matching settings.EMBEDDING_DIM) for local similarity search.
        """
        if dim is None:
            dim = settings.EMBEDDING_DIM
        words = re.findall(r'\w+', text.lower())
        vec = np.zeros(dim, dtype=np.float32)
        if not words:
            return vec.tolist()
        
        for word in words:
            idx = abs(hash(word)) % dim
            vec[idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def _generate_local_grounded_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Generates a grounded academic explanation directly from retrieved textbook excerpts.
        """
        if not chunks:
            return "I searched the uploaded textbook, but could not find information matching your question."

        top_chunk = chunks[0]
        page_num = top_chunk.get("page", 1)
        text_content = top_chunk.get("text", "")

        answer_lines = [
            f"### Explanation from Textbook (Page {page_num})",
            "",
            f"Based on **Page {page_num}** of your uploaded textbook:",
            "",
            f"> \"{text_content[:400]}...\"",
            "",
            "#### Key Takeaways:",
        ]

        # Extract sentences matching question keywords
        keywords = set(re.findall(r'\w+', question.lower())) - {'what', 'is', 'the', 'how', 'why', 'in', 'on', 'a', 'an', 'of', 'for', 'to'}
        matching_sentences = []

        for c in chunks[:3]:
            sentences = re.split(r'(?<=[.!?])\s+', c.get("text", ""))
            for s in sentences:
                if any(kw in s.lower() for kw in keywords) and len(s) > 20:
                    matching_sentences.append(f"- **[Page {c.get('page', 1)}]**: {s.strip()}")

        if matching_sentences:
            answer_lines.extend(matching_sentences[:4])
        else:
            answer_lines.append(f"- **Summary**: The textbook discusses this concept on **Page {page_num}**.")

        return "\n".join(answer_lines)

llm_service = LLMService()

