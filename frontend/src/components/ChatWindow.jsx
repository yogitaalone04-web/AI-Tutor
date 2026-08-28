import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import { BookOpen, RefreshCw, Sparkles, MessageSquare } from 'lucide-react';

export default function ChatWindow({
  messages,
  isLoading,
  bookInfo,
  onResetSession,
  onSelectStarter
}) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const starterQuestions = [
    "Summarize the key concepts covered in chapter 1.",
    "Explain the main theories or equations step-by-step.",
    "Give me 3 practice quiz questions based on this textbook.",
    "What are the core definitions I should memorize for an exam?"
  ];

  return (
    <div className="chat-container">
      {/* Header Bar */}
      <div className="chat-bar-header">
        <div className="book-info">
          <div className="book-icon-badge">
            <BookOpen size={18} />
          </div>
          <div>
            <div className="book-title-text">{bookInfo?.filename || "Uploaded Textbook"}</div>
            <div className="book-meta-text">
              {bookInfo?.total_pages ? `${bookInfo.total_pages} Pages` : ''} 
              {bookInfo?.total_chunks ? ` • ${bookInfo.total_chunks} Chunks Indexed` : ''}
            </div>
          </div>
        </div>

        <button className="btn-reset" onClick={onResetSession} title="Upload a different textbook">
          <RefreshCw size={14} /> Change Book
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="messages-list">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <div className="empty-icon">
              <Sparkles size={28} />
            </div>
            <h3 className="empty-title">Ready to Study!</h3>
            <p className="empty-desc">
              Your textbook has been processed and indexed. Ask any question below or click a starter suggestion to begin.
            </p>

            <div className="starters-grid">
              {starterQuestions.map((q, idx) => (
                <div key={idx} className="starter-card" onClick={() => onSelectStarter(q)}>
                  <MessageSquare size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0, marginTop: '2px' }} />
                  <span>{q}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))
        )}

        {/* LLM Thinking/Typing State */}
        {isLoading && (
          <div className="message-bubble assistant">
            <div className="avatar assistant">
              <Sparkles size={18} />
            </div>
            <div className="bubble-content" style={{ padding: '0.75rem 1rem' }}>
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                  Searching textbook & crafting explanation...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
