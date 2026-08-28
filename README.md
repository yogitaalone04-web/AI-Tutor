# 🎓 AI Tutor — Textbook Q&A Assistant

**Teacher Assessment Tool (TAE-I) — Project Based Learning**  
*Prepared for:* **S.B. Jain Institute of Technology, Management and Research, Nagpur**  
*Prepared by:* **Yogita — B.Tech CSE (2024–2027)**  
*Document Version:* 1.0  

---

## 📌 Overview

**AI Tutor** is a web-based Retrieval-Augmented Generation (RAG) application. Students can upload an academic textbook (PDF), and the system extracts, chunks, and indexes the content in a vector store (`FAISS`). Students can then ask natural language academic questions, receiving explanations strictly grounded in the textbook content using Google Gemini (`gemini-1.5-flash` & `gemini-embedding-001`).

---

## ✨ Features

- 📄 **Textbook PDF Ingestion**: Page-by-page text extraction (`pdfplumber` with fallback to `PyPDF2`).
- 🧩 **Smart Text Chunking**: Sliding window overlap chunking (~500 tokens / 1500 chars) retaining page number metadata.
- ⚡ **FAISS Vector Store**: Fast in-memory similarity search per upload session.
- 🎯 **Grounded Q&A (RAG)**: Fixed academic tutor system prompt preventing hallucinations and citing page references (e.g., `[Page 14]`).
- 🎨 **Modern Dark Academic UI**: React (Vite) interface featuring glassmorphism, animated upload progress, Markdown formatting (`react-markdown`), code blocks, copy-to-clipboard, and responsive layouts.
- 🐳 **Docker-Ready**: Standardized `docker-compose.yml` configuration for seamless containerized deployment.

---

## 📁 Repository Structure

```text
ai-tutor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entrypoint
│   │   ├── routes/
│   │   │   ├── upload.py           # POST /api/upload route
│   │   │   └── chat.py             # POST /api/chat & GET /api/health
│   │   ├── services/
│   │   │   ├── ingestion_service.py # PDF text extraction & chunking
│   │   │   ├── vectorstore_service.py # FAISS index management
│   │   │   └── llm_service.py      # Gemini embeddings & prompt generation
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic data schemas
│   │   ├── core/
│   │   │   └── config.py           # Configuration & settings
│   │   └── db/
│   │       └── database.py         # Database initialization helper
│   ├── storage/
│   │   └── uploads/                # Temporary storage for uploaded PDFs
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadBox.jsx       # PDF upload dropzone & progress
│   │   │   ├── ChatWindow.jsx      # Chat messages list & starters
│   │   │   ├── MessageBubble.jsx   # Markdown bubble with page citations
│   │   │   └── InputBox.jsx        # Question text area & send button
│   │   ├── pages/
│   │   │   └── Home.jsx            # Main dashboard container
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 🛠️ Local Setup & Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & `npm`
- **Google Gemini API Key** (Get a free key from [Google AI Studio](https://aistudio.google.com/))

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and add your GEMINI_API_KEY=your_key_here

# Run backend development server
uvicorn app.main:app --reload --port 8000
```
Backend will be available at: `http://localhost:8000` (API Docs: `http://localhost:8000/docs`).

---

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend application will be available at: `http://localhost:5173`.

---

### 3. Docker Run (Alternative)

Run both backend and frontend together with a single command:

```bash
# Set your Gemini API key in your environment
export GEMINI_API_KEY=your_key_here  # Linux/Mac
$env:GEMINI_API_KEY="your_key_here"  # Windows PowerShell

# Build and start services
docker-compose up --build
```

---

## 🔌 API Reference

### 1. Health Check
`GET /api/health`
- **Response**: `{ "status": "ok", "version": "1.0.0" }`

### 2. Upload Textbook PDF
`POST /api/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (PDF file, max 20MB)
- **Response**:
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "ready",
  "filename": "operating_systems.pdf",
  "total_pages": 42,
  "total_chunks": 118
}
```

### 3. Chat with Textbook
`POST /api/chat`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "question": "What is deadlocking in process management?"
}
```
- **Response**:
```json
{
  "answer": "Deadlock is a situation where a set of processes are blocked because each process holds a resource and waits for another resource held by another process...\n\n**Key Conditions:**\n1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait",
  "sources": [
    { "page": 14, "snippet": "A deadlock occurs when processes are unable to proceed because..." }
  ]
}
```

---

## 🚀 Deployment Guide

### Deploying Backend (Render / Railway)
1. Push repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com) or [Railway](https://railway.app).
3. Connect repository and select root directory `/backend`.
4. Build Command: `pip install -r requirements.txt`.
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add Environment Variable: `GEMINI_API_KEY` = your Gemini key.

### Deploying Frontend (Vercel / Netlify)
1. Create a new project on [Vercel](https://vercel.com).
2. Connect repository and select root directory `/frontend`.
3. Framework Preset: **Vite**.
4. Add Environment Variable: `VITE_API_BASE_URL` = `https://your-backend.onrender.com/api`.
5. Deploy!

---

## 📊 TAE-I Assessment Mapping

| Rubric Criteria | Marks | How This Project Meets It |
| :--- | :---: | :--- |
| **Topic Knowledge** | **3M** | Detailed SRS architecture, RAG vector retrieval concepts, and Gemini LLM integration. |
| **Development** | **3M** | Complete full-stack application: React + FastAPI + FAISS + Gemini API with page citations & error handling. |
| **Presentation** | **2M** | Live demo ready UI with drag-and-drop upload, animated processing, and markdown chat bubbles. |
| **Report** | **2M** | Comprehensive SRS & README documentation formatted per academic requirements. |
