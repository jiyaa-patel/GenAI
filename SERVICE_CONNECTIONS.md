# Service Connections Configuration

## Production URLs
- **Frontend**: https://genai-silk-beta.vercel.app/
- **Django Backend**: https://gen-ai-legal.uc.r.appspot.com
- **FastAPI Service**: https://fastapi-dot-gen-ai-legal.uc.r.appspot.com

## Service Architecture

### Frontend (React + Vite)
- **Hosted on**: Vercel
- **Connects to**: 
  - Django Backend for authentication and user management
  - FastAPI Service for document processing and AI chat

### Django Backend
- **Hosted on**: Google App Engine (default service)
- **Handles**:
  - User authentication (login, signup, Google OAuth)
  - User management
  - Chat session persistence
  - Message history storage
- **Database**: PostgreSQL on Google Cloud SQL

### FastAPI Service
- **Hosted on**: Google App Engine (fastapi service)
- **Handles**:
  - PDF document upload and processing
  - AI-powered document analysis
  - Real-time chat with documents
  - Vector embeddings and search
- **Storage**: Google Cloud Storage for documents and vectors

## API Endpoints

### Django Backend (Authentication & Data)
- `POST /api/login/` - User login
- `POST /api/signup/` - User registration
- `POST /api/google-login/` - Google OAuth login
- `GET /api/geniai/chat-sessions/` - Get user's chat sessions
- `GET /api/geniai/chat-sessions/{id}/messages/` - Get chat messages
- `POST /api/geniai/chat-sessions/{id}/messages/` - Save chat message

### FastAPI Service (Document Processing & AI)
- `POST /api/upload-document` - Upload and process PDF documents
- `POST /api/ask-question` - Ask questions about uploaded documents
- `GET /api/chat-sessions` - Get chat sessions (FastAPI backup)
- `GET /api/chat-history/{chat_id}` - Get chat history (FastAPI backup)

## Environment Variables

### Frontend (.env.production)
```
VITE_GOOGLE_CLIENT_ID="488637618552-fs78i0lr0tul8qo38dmt45mn5hm3h50q.apps.googleusercontent.com"
VITE_DJANGO_BASE_URL="https://gen-ai-legal.uc.r.appspot.com"
VITE_FASTAPI_BASE_URL="https://fastapi-dot-gen-ai-legal.uc.r.appspot.com"
```

### Django Backend (app.yaml)
```yaml
env_variables:
  GCP_PROJECT: "gen-ai-legal"
  GCS_BUCKET_NAME: "legal-agreement-analyzer-gen-ai-legal"
```

### FastAPI Service (fastapi.yaml)
```yaml
env_variables:
  GCP_PROJECT: "gen-ai-legal"
  GCS_BUCKET_NAME: "legal-agreement-analyzer-gen-ai-legal"
  GEMINI_API_KEY: "AIzaSyANsEjkReSfVGOkXg3v3XS82UXoaz7J95A"
```

## CORS Configuration

All services are configured to allow cross-origin requests between:
- Frontend: https://genai-silk-beta.vercel.app
- Django: https://gen-ai-legal.uc.r.appspot.com
- FastAPI: https://fastapi-dot-gen-ai-legal.uc.r.appspot.com

## Data Flow

1. **User Authentication**: Frontend → Django Backend
2. **Document Upload**: Frontend → FastAPI Service
3. **Document Processing**: FastAPI Service → Google Cloud Storage
4. **Chat Sessions**: FastAPI Service → Django Backend (sync)
5. **AI Queries**: Frontend → FastAPI Service
6. **Message Storage**: FastAPI Service → Django Backend + GCS

## Deployment Commands

### Django Backend
```bash
gcloud app deploy app.yaml
```

### FastAPI Service
```bash
cd Final_Backend/geniai
gcloud app deploy fastapi.yaml
```

### Frontend (Vercel)
- Connected to GitHub repository
- Auto-deploys on push to main branch
- Environment variables configured in Vercel dashboard