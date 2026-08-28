from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, SourceCitation, ErrorResponse
from app.services.vectorstore_service import vectorstore_service
from app.services.llm_service import llm_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Uptime health check endpoint.
    """
    return HealthResponse(status="ok", version="1.0.0")

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Session not found"},
        502: {"model": ErrorResponse, "description": "LLM Service API failure"}
    }
)
async def chat_with_tutor(req: ChatRequest):
    """
    Accepts a student question and session ID, performs RAG retrieval from the
    uploaded textbook's FAISS index, and generates a grounded response using Gemini.
    """
    # 1. Validate session
    if not vectorstore_service.has_session(req.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired. Please upload a textbook first."
        )

    # 2. Embed student question
    try:
        query_embedding = llm_service.generate_query_embedding(req.question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error embedding question: {str(e)}"
        )

    # 3. Retrieve relevant chunks from FAISS
    try:
        retrieved_chunks = vectorstore_service.search(
            session_id=req.session_id,
            query_embedding=query_embedding,
            top_k=5
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}"
        )

    # 4. Generate grounded tutor response via Gemini LLM
    try:
        answer_text = llm_service.generate_answer(
            question=req.question,
            retrieved_chunks=retrieved_chunks
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM Tutor Service Error: {str(e)}"
        )

    # 5. Extract citations
    sources = []
    seen_pages = set()
    for chunk in retrieved_chunks:
        page = chunk.get("page", 1)
        if page not in seen_pages:
            seen_pages.add(page)
            snippet = chunk.get("text", "")[:120].strip() + "..."
            sources.append(SourceCitation(page=page, snippet=snippet))

    return ChatResponse(answer=answer_text, sources=sources)
