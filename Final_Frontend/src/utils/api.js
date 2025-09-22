import { useGoogleLogin } from '@react-oauth/google';

// Simple API client for Django (auth) and FastAPI (documents/chat)
const DJANGO_BASE_URL = import.meta.env.VITE_DJANGO_BASE_URL || 'http://localhost:8000';
const FASTAPI_BASE_URL = import.meta.env.VITE_FASTAPI_BASE_URL || 'http://localhost:8001';

console.log('=== API Configuration ===');
console.log('Django URL:', DJANGO_BASE_URL);
console.log('FastAPI URL:', FASTAPI_BASE_URL);
console.log('Environment:', import.meta.env.MODE);
console.log('========================');

function getAuthHeaders() {
  const token = localStorage.getItem('accessToken');
  const userEmail = localStorage.getItem('userEmail');
  const csrfToken = getCsrfToken();
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (userEmail) headers['x-user-email'] = userEmail;
  if (csrfToken) headers['X-CSRFToken'] = csrfToken;
  return headers;
}

function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function refreshAccessTokenIfNeeded(response) {
  if (response && response.status === 401) {
    const refresh = localStorage.getItem('refreshToken');
    if (!refresh) return null;
    const r = await fetch(`${DJANGO_BASE_URL}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });
    if (!r.ok) return null;
    const data = await r.json();
    if (data && data.access) {
      localStorage.setItem('accessToken', data.access);
      return data.access;
    }
  }
  return null;
}

async function fetchWithAuth(url, options = {}) {
  const initialHeaders = { ...(options.headers || {}), ...getAuthHeaders() };
  const isDjangoUrl = url.includes(DJANGO_BASE_URL);
  
  const requestOptions = {
    ...options,
    headers: initialHeaders,
    ...(isDjangoUrl && { credentials: 'include' })
  };
  
  let res = await fetch(url, requestOptions);
  if (res.status === 401) {
    const newAccess = await refreshAccessTokenIfNeeded(res);
    if (newAccess) {
      const userEmail = localStorage.getItem('userEmail');
      const retryHeaders = { 
        ...(options.headers || {}), 
        Authorization: `Bearer ${newAccess}`,
        ...(userEmail && { 'x-user-email': userEmail })
      };
      const retryOptions = {
        ...options,
        headers: retryHeaders,
        ...(isDjangoUrl && { credentials: 'include' })
      };
      res = await fetch(url, retryOptions);
      if (res.status === 401) {
        // Token refresh failed, force logout
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userEmail');
        window.location.href = '/login';
        throw new Error('Authentication failed. Please log in again.');
      }
    } else {
      // No refresh token or refresh failed
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userEmail');
      window.location.href = '/login';
      throw new Error('Authentication failed. Please log in again.');
    }
  }
  return res;
}

export const authApi = {
  async login(email, password) {
    const res = await fetch(`${DJANGO_BASE_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      let errorDetail = 'Login failed';
      try {
        const errorData = await res.json();
        errorDetail = errorData.error || errorData.detail || `Login failed (${res.status})`;
      } catch (_) {
        errorDetail = `Login failed (${res.status})`;
      }
      throw new Error(errorDetail);
    }
    return res.json();
  },

  async signup(payload) {
    const signupUrl = `${DJANGO_BASE_URL}/api/signup/`;
    console.log('Signup URL:', signupUrl);
    console.log('DJANGO_BASE_URL:', DJANGO_BASE_URL);
    const res = await fetch(signupUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      let errorDetail = 'Signup failed';
      try {
        const errorData = await res.json();
        errorDetail = errorData.error || errorData.detail || `Signup failed (${res.status})`;
      } catch (_) {
        errorDetail = `Signup failed (${res.status})`;
      }
      throw new Error(errorDetail);
    }
    return res.json();
  },

  async googleLogin(token) {
    const googleLoginUrl = `${DJANGO_BASE_URL}/api/google-login/`;
    console.log('Google Login URL:', googleLoginUrl);
    const res = await fetch(googleLoginUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
    if (!res.ok) throw new Error('Google login failed');
    return res.json();
  },

  async me() {
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/protected/`, {
      headers: { ...getAuthHeaders() }
    });
    return res;
  },

  async forgotPassword(email) {
    const res = await fetch(`${DJANGO_BASE_URL}/api/forgot-password/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) {
      let errorDetail = 'Forgot password failed';
      try {
        const errorData = await res.json();
        errorDetail = errorData.error || errorData.detail || `Request failed (${res.status})`;
      } catch (_) {
        errorDetail = `Request failed (${res.status})`;
      }
      throw new Error(errorDetail);
    }
    return res.json();
  },

  async resetPassword(email, token, newPassword) {
    const res = await fetch(`${DJANGO_BASE_URL}/api/reset-password/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, token, new_password: newPassword })
    });
    if (!res.ok) {
      let errorDetail = 'Password reset failed';
      try {
        const errorData = await res.json();
        errorDetail = errorData.error || errorData.detail || `Reset failed (${res.status})`;
      } catch (_) {
        errorDetail = `Reset failed (${res.status})`;
      }
      throw new Error(errorDetail);
    }
    return res.json();
  },
};

export const legalApi = {
  async uploadDocument(file) {
    const uploadUrl = `${FASTAPI_BASE_URL}/api/upload-document`;
    console.log('Uploading to:', uploadUrl);
    console.log('Auth headers:', getAuthHeaders());
    
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(uploadUrl, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: formData,
    });
    
    console.log('Upload response status:', res.status);
    
    if (!res.ok) {
      let detail = '';
      try {
        detail = await res.text();
        console.error('Upload error detail:', detail);
      } catch (_) {}
      throw new Error(`Upload failed (${res.status}): ${detail}`);
    }
    return res.json();
  },

  async askQuestion(query, chatId, documentId) {
    const res = await fetch(`${FASTAPI_BASE_URL}/api/ask-question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ query, chat_id: chatId || null, document_id: documentId || null })
    });
    if (!res.ok) {
      let detail = '';
      try { detail = await res.text(); } catch (_) {}
      throw new Error(`Question failed (${res.status}): ${detail}`);
    }
    return res.json();
  },

  async saveMessage(chatSessionId, content, messageType) {
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/geniai/chat-sessions/${chatSessionId}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ content, message_type: messageType })
    });
    if (!res.ok) throw new Error('Save message failed');
    return res.json();
  },

  async getChatSessions() {
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/geniai/chat-sessions/list/`, {
      headers: { ...getAuthHeaders() },
    });
    if (!res.ok) throw new Error('Fetch sessions failed');
    return res.json();
  },

  async getChatMessages(chatSessionId) {
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/geniai/chat-sessions/${chatSessionId}/messages/`, {
      headers: { ...getAuthHeaders() },
    });
    if (!res.ok) throw new Error('Fetch messages failed');
    return res.json();
  },

  async createChatSession(name = 'New Chat', documentId = null) {
    const payload = { name };
    if (documentId) payload.document_id = documentId;
    
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/geniai/chat-sessions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      let detail = '';
      try { detail = await res.text(); } catch (_) {}
      throw new Error(`Create session failed (${res.status}): ${detail}`);
    }
    return res.json();
  },

  async getSessionsWithMessages() {
    const res = await fetchWithAuth(`${DJANGO_BASE_URL}/api/geniai/chat-sessions/with-messages/`, {
      headers: { ...getAuthHeaders() },
    });
    if (!res.ok) throw new Error('Fetch sessions with messages failed');
    return res.json();
  }
};

export { DJANGO_BASE_URL, FASTAPI_BASE_URL };


