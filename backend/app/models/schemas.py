from typing import List, Optional
from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    session_id: str
    status: str
    filename: str
    total_pages: int
    total_chunks: int

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Active session ID from textbook upload")
    question: str = Field(..., min_length=1, description="Student's academic question")

class SourceCitation(BaseModel):
    page: int
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceCitation]] = []

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"

class ErrorResponse(BaseModel):
    error: str
