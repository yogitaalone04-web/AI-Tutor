import os
from typing import List, Dict, Any, Tuple
import pdfplumber
import PyPDF2
from app.core.config import settings

class IngestionService:
    """
    Service for extracting text from textbook PDFs and chunking text into overlapping passages
    ready for embedding with gemini-embedding-001 and indexing into FAISS.
    """
    @staticmethod
    def extract_text_by_pages(pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extracts text from a PDF file page by page.
        Returns a list of tuples: [(page_number, text), ...]
        """
        pages_text: List[Tuple[int, str]] = []
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text = text.strip()
                    if text:
                        pages_text.append((idx + 1, text))
        except Exception as e:
            print(f"[IngestionService] pdfplumber failed: {e}. Falling back to PyPDF2...")
            pages_text = []

        # Fallback to PyPDF2 if pdfplumber extracted nothing or failed
        if not pages_text:
            try:
                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for idx, page in enumerate(reader.pages):
                        text = page.extract_text() or ""
                        text = text.strip()
                        if text:
                            pages_text.append((idx + 1, text))
            except Exception as e:
                print(f"[IngestionService] PyPDF2 extraction failed: {e}")
                raise ValueError("Could not extract readable text from the PDF. The PDF may be scanned or corrupted.")

        if not pages_text:
            raise ValueError("The uploaded PDF does not contain extractable text. Please upload a digital textbook PDF.")

        return pages_text

    @staticmethod
    def chunk_text(pages_text: List[Tuple[int, str]], chunk_size: int = None, chunk_overlap: int = None) -> List[Dict[str, Any]]:
        """
        Splits extracted page texts into overlapping chunks while tracking source page numbers.
        Returns a list of dicts: [{"id": int, "text": str, "page": int}]
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP

        chunks: List[Dict[str, Any]] = []
        chunk_counter = 0

        for page_num, text in pages_text:
            if not text:
                continue

            # Slide window over page text
            start = 0
            text_len = len(text)

            while start < text_len:
                end = start + chunk_size
                chunk_str = text[start:end].strip()

                if chunk_str:
                    chunks.append({
                        "id": chunk_counter,
                        "text": chunk_str,
                        "page": page_num
                    })
                    chunk_counter += 1

                start += (chunk_size - chunk_overlap)
                if start >= text_len or end >= text_len:
                    break

        return chunks

ingestion_service = IngestionService()
