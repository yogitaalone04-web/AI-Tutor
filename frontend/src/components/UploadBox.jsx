import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, Sparkles, BookOpen } from 'lucide-react';

export default function UploadBox({ onUploadSuccess, isProcessing, setIsProcessing, setError }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [stepMessage, setStepMessage] = useState("Reading textbook content...");
  const fileInputRef = useRef(null);

  const validateAndSetFile = (file) => {
    setError(null);
    if (!file) return;

    if (!file.name.toLowerCase().endswith?.('.pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
      setError("Only PDF files (.pdf) are supported. Please select a valid textbook PDF.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("File size exceeds 20 MB limit. Please select a smaller PDF.");
      return;
    }

    setSelectedFile(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);
    setStepMessage("Reading textbook pages & extracting text...");

    // Simulated progress steps for enhanced UX
    const timer1 = setTimeout(() => setStepMessage("Chunking text & calculating embeddings..."), 2500);
    const timer2 = setTimeout(() => setStepMessage("Indexing vector store for retrieval..."), 5500);

    try {
      await onUploadSuccess(selectedFile);
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      setIsProcessing(false);
    }
  };

  return (
    <div className="upload-wrapper">
      <div className="upload-hero">
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(99, 102, 241, 0.15)', padding: '0.35rem 0.85rem', borderRadius: '9999px', fontSize: '0.85rem', color: '#a5b4fc', marginBottom: '1rem', fontWeight: 500 }}>
          <Sparkles size={16} /> RAG-Powered AI Tutor
        </div>
        <h1>Upload Your Textbook</h1>
        <p>Ask natural language questions and get clear explanations grounded strictly in your study material.</p>
      </div>

      {isProcessing ? (
        <div className="processing-card">
          <div className="pulse-spinner"></div>
          <h3 className="processing-title">Reading Your Textbook...</h3>
          <p className="processing-step">{stepMessage}</p>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill"></div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            style={{ display: 'none' }}
          />

          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="dropzone-icon-wrapper">
              <BookOpen size={32} />
            </div>

            {selectedFile ? (
              <div>
                <h3 className="dropzone-title" style={{ color: '#a5b4fc' }}>{selectedFile.name}</h3>
                <p className="dropzone-subtitle">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze
                </p>
              </div>
            ) : (
              <div>
                <h3 className="dropzone-title">Drag & Drop your textbook PDF here</h3>
                <p className="dropzone-subtitle">Supports text-based PDF files up to 20 MB</p>
              </div>
            )}

            <button
              type="button"
              className="btn-select"
              onClick={(e) => {
                e.stopPropagation();
                if (selectedFile) {
                  handleSubmit(e);
                } else {
                  fileInputRef.current?.click();
                }
              }}
            >
              {selectedFile ? (
                <>
                  <Upload size={18} /> Start Studying
                </>
              ) : (
                <>
                  <FileText size={18} /> Browse Computer
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
