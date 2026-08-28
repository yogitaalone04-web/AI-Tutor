import axios from 'axios';

// Get base URL from environment or default to local FastAPI dev server
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s timeout for PDF processing/LLM generation
});

export const api = {
  /**
   * Uploads a textbook PDF file to the backend
   * @param {File} file - PDF file to upload
   */
  async uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Sends a student question to the RAG backend
   * @param {string} sessionId - Active session ID
   * @param {string} question - Question text
   */
  async sendQuestion(sessionId, question) {
    const response = await apiClient.post('/chat', {
      session_id: sessionId,
      question: question,
    });
    return response.data;
  },

  /**
   * Health check for backend server status
   */
  async checkHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
