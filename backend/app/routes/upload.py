import uuid
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings, STORAGE_DIR
from app.models.schemas import UploadResponse, ErrorResponse
from app.services.ingestion_service import ingestion_service
from app.services.vectorstore_service import vectorstore_service
from app.services.llm_service import llm_service

router = APIRouter()

@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type or size limit exceeded"},
        500: {"model": ErrorResponse, "description": "PDF processing failure"}
    }
)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a textbook PDF upload, extracts text, chunks it, generates embeddings,
    and indexes them in FAISS under a unique session ID.
    """
    # 1. Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file (.pdf)."
        )

    # 2. Save temporary file & validate size
    session_id = str(uuid.uuid4())
    temp_filename = f"{session_id}_{file.filename}"
    temp_path = os.path.join(STORAGE_DIR, temp_filename)

    try:
        file_size = 0
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    # Clean up temp file
                    buffer.close()
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                buffer.write(chunk)

        # 3. Extract text from PDF page by page
        try:
            pages_text = ingestion_service.extract_text_by_pages(temp_path)
        except ValueError as val_err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read PDF content: {str(e)}"
            )

        # 4. Chunk text with page tracking
        chunks = ingestion_service.chunk_text(pages_text)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text content found in the PDF."
            )

        # 5. Generate chunk embeddings
        chunk_texts = [c["text"] for c in chunks]
        try:
            embeddings = llm_service.generate_embeddings(chunk_texts)
        except Exception as embed_err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Embedding Service Error: {str(embed_err)}"
            )

        # 6. Build FAISS index in vector store service
        total_pages = max([p for p, _ in pages_text]) if pages_text else 1
        vectorstore_service.create_session_index(
            session_id=session_id,
            embeddings=embeddings,
            chunks=chunks,
            filename=file.filename,
            total_pages=total_pages
        )

        return UploadResponse(
            session_id=session_id,
            status="ready",
            filename=file.filename,
            total_pages=total_pages,
            total_chunks=len(chunks)
        )

    finally:
        # Clean up temp PDF file on disk
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
