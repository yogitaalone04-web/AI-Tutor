import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

export default function InputBox({ onSend, isLoading, disabled }) {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [question]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isLoading || disabled) return;
    onSend(question.trim());
    setQuestion('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-box-wrapper">
      <textarea
        ref={textareaRef}
        rows={1}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Please upload a textbook PDF first..." : "Ask your tutor anything about the textbook..."}
        disabled={disabled || isLoading}
        className="chat-textarea"
      />
      <button
        type="submit"
        disabled={!question.trim() || isLoading || disabled}
        className="btn-send"
        title="Send Question"
      >
        {isLoading ? (
          <div style={{
            width: '16px',
            height: '16px',
            border: '2px solid rgba(255,255,255,0.3)',
            borderTopColor: '#ffffff',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }} />
        ) : (
          <Send size={18} />
        )}
      </button>
    </form>
  );
}
