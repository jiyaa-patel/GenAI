# URL Mapping - Frontend ↔ Backend

## **Django Backend URLs (Port 8000)**

### **Authentication APIs** (`/api/`)
- `POST /api/login/` → `authApi.login()`
- `POST /api/signup/` → `authApi.signup()`
- `POST /api/google-login/` → `authApi.googleLogin()`
- `POST /api/token/refresh/` → Auto-called in `fetchWithAuth()`
- `GET /api/protected/` → `authApi.me()`
- `POST /api/forgot-password/` → `authApi.forgotPassword()`
- `POST /api/reset-password/` → `authApi.resetPassword()`

### **GenAI APIs** (`/api/geniai/`)
- `POST /api/geniai/documents/` → Django sync only
- `POST /api/geniai/chat-sessions/` → `legalApi.createChatSession()`
- `GET /api/geniai/chat-sessions/list/` → `legalApi.getChatSessions()`
- `GET /api/geniai/chat-sessions/{id}/messages/` → `legalApi.getChatMessages()`
- `GET /api/geniai/chat-sessions/with-messages/` → `legalApi.getSessionsWithMessages()`
- `POST /api/geniai/chat-messages/` → Django sync only
- `POST /api/geniai/summaries/` → Django sync only
- `GET /api/geniai/current-user/` → Available
- `GET /api/geniai/test/` → Test endpoint

## **FastAPI Backend URLs (Port 8001)**

### **Document & Chat APIs** (`/api/`)
- `POST /api/upload-document` → `legalApi.uploadDocument()`
- `POST /api/ask-question` → `legalApi.askQuestion()`
- `GET /api/chat-sessions` → Available (local storage)
- `GET /api/chat-history/{chat_id}` → Available (local storage)
- `GET /api/health` → Health check

## **Frontend API Usage**

### **Authentication Flow**
```javascript
// Login
const result = await authApi.login(email, password);
localStorage.setItem('accessToken', result.access);
localStorage.setItem('userEmail', result.email);

// Auto token refresh in all requests
const response = await fetchWithAuth(url, options);
```

### **Document Upload & Chat Flow**
```javascript
// 1. Upload document (FastAPI)
const uploadResult = await legalApi.uploadDocument(file);
// Returns: { chat_id, document_id, chat_name }

// 2. Ask questions (FastAPI)
const response = await legalApi.askQuestion(query, chatId, documentId);

// 3. Get chat history (Django)
const messages = await legalApi.getChatMessages(chatSessionId);

// 4. Get all sessions (Django)
const sessions = await legalApi.getChatSessions();
```

## **Headers Sent by Frontend**
```javascript
{
  'Authorization': 'Bearer {token}',
  'x-user-email': '{user_email}',
  'Content-Type': 'application/json'
}
```

## **Data Flow**
1. **User uploads document** → FastAPI processes → Saves to GCS → Syncs to Django DB
2. **User asks question** → FastAPI queries GCS → Syncs messages to Django DB  
3. **Frontend loads chat history** → Django DB returns user-specific data
4. **All data isolated by user** → Both GCS paths and DB records filtered by user

## **Environment Variables**
```javascript
// Frontend (.env)
VITE_DJANGO_BASE_URL=http://localhost:8000
VITE_FASTAPI_BASE_URL=http://localhost:8001

// Backend (.env)
GCS_BUCKET_NAME=legal-agreement-analyzer
DJANGO_BASE_URL=http://localhost:8000
```