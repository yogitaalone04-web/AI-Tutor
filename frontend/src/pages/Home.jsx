import React, { useState, useEffect } from 'react';
import UploadBox from '../components/UploadBox';
import ChatWindow from '../components/ChatWindow';
import InputBox from '../components/InputBox';
import { api } from '../services/api';
import { GraduationCap, AlertCircle, RefreshCw } from 'lucide-react';

export default function Home() {
  const [sessionId, setSessionId] = useState(null);
  const [bookInfo, setBookInfo] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const [isUploading, setIsUploading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  // Initial health check
  useEffect(() => {
    api.checkHealth()
      .then(() => setIsBackendOnline(true))
      .catch((err) => {
        console.warn("Backend health check warning:", err);
        // Note: Keep online state accessible for local dev
      });
  }, []);

  const handleUploadSuccess = async (file) => {
    try {
      const data = await api.uploadPDF(file);
      setSessionId(data.session_id);
      setBookInfo({
        filename: data.filename,
        total_pages: data.total_pages,
        total_chunks: data.total_chunks
      });
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error("Upload error:", err);
      const errMsg = err.response?.data?.detail || err.message || "Failed to process PDF. Please make sure backend is running with a valid GEMINI_API_KEY.";
      setError(errMsg);
      throw err;
    }
  };

  const handleSendQuestion = async (questionText) => {
    if (!sessionId) return;

    const userMsg = { role: 'user', content: questionText };
    setMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);
    setError(null);

    try {
      const data = await api.sendQuestion(sessionId, questionText);
      const botMsg = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || []
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      const errMsg = err.response?.data?.detail || err.message || "Could not reach the tutor. Please check network connectivity or try again.";
      setError(errMsg);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleResetSession = () => {
    setSessionId(null);
    setBookInfo(null);
    setMessages([]);
    setError(null);
  };

  return (
    <div className="app-container">
      {/* App Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">
            <GraduationCap size={24} />
          </div>
          <div>
            <div className="brand-title">AI Tutor</div>
            <div className="brand-subtitle">Textbook Q&A Assistant • S.B. Jain Institute</div>
          </div>
        </div>

        <div className="header-badge">
          <span className="status-dot"></span>
          <span>{isBackendOnline ? "Tutor Engine Ready" : "Connecting..."}</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Error Banner */}
        {error && (
          <div className="error-banner">
            <div className="error-left">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              style={{ background: 'transparent', border: 'none', color: '#fca5a5', cursor: 'pointer', fontWeight: 'bold' }}
            >
              Dismiss
            </button>
          </div>
        )}

        {!sessionId ? (
          <UploadBox
            onUploadSuccess={handleUploadSuccess}
            isProcessing={isUploading}
            setIsProcessing={setIsUploading}
            setError={setError}
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%', overflow: 'hidden' }}>
            <ChatWindow
              messages={messages}
              isLoading={isChatLoading}
              bookInfo={bookInfo}
              onResetSession={handleResetSession}
              onSelectStarter={handleSendQuestion}
            />
            <div className="input-area-container">
              <InputBox
                onSend={handleSendQuestion}
                isLoading={isChatLoading}
                disabled={!sessionId}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
