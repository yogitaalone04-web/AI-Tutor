from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import upload, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Tutor — Textbook Q&A Assistant",
    version="1.0.0"
)

# CORS Configuration
origins = [
    settings.ALLOWED_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"  # Allow all for flexible testing/deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(upload.router, prefix=settings.API_V1_STR, tags=["Upload"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["Chat"])

@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
