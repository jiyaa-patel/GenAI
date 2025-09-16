-- Users table to store user information
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Documents table to store uploaded legal documents
CREATE TABLE documents (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agreement_type VARCHAR(100),
    word_count INTEGER
);

-- Document summaries table
CREATE TABLE document_summaries (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) REFERENCES documents(id),
    summary TEXT,
    agreement_type VARCHAR(100),
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) REFERENCES documents(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);

-- Chat messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id VARCHAR(255) REFERENCES chat_sessions(id),
    is_user BOOLEAN NOT NULL,  -- true if message is from user, false if from AI
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks table for vector search
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768)  -- Adjust dimension based on your embedding model
);

-- Create indexes for performance
CREATE INDEX idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);

-- Add vector search capability (requires pg_vector extension)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_l2_ops);# Legal Agreement Analyzer API

A FastAPI-based service for analyzing legal agreements using AI-powered chat functionality with automatic chat naming.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GCP_PROJECT=your_gcp_project_id
GCP_LOCATION=us-central1
GCS_BUCKET_NAME=your-gcs-bucket-name
```

### 3. Set up Google Cloud Services
- **Google Cloud Storage**: Create a bucket for storing documents, FAISS indices, and chat sessions
- **Authentication**: Set up service account with proper permissions

### 4. Start the API
```bash
python api.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs

## Core Files

- **`api.py`** - Main FastAPI application
- **`chat_naming.py`** - AI-powered chat naming functionality
- **`agreement_analyzer.py`** - Legal document analysis
- **`create_db.py`** - Document processing and embeddings
- **`query.py`** - Query processing for command-line usage
- **`requirements.txt`** - Python dependencies

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload-document` | POST | Upload PDF, get chat_id & initial summary |
| `/api/ask-question` | POST | Ask questions or get detailed summary |
| `/api/chat-sessions` | GET | Get all chat sessions |
| `/api/generate-chat-name` | POST | Generate chat names |
| `/api/health` | GET | Health check |

## Usage Example

```bash
# Upload document (with user_id)
curl -X POST "http://localhost:8000/api/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employment_contract.pdf" \
  -F "user_id=user123"

# Get detailed summary
curl -X POST "http://localhost:8000/api/ask-question" \
  -H "Content-Type: application/json" \
  -d '{"query": "summary", "chat_id": "chat-uuid", "user_id": "user123"}'

# Ask questions
curl -X POST "http://localhost:8000/api/ask-question" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key terms?", "chat_id": "chat-uuid", "user_id": "user123"}'

# Get user's chat sessions
curl -X GET "http://localhost:8000/api/chat-sessions?user_id=user123"
```

## Workflow

1. **Upload legal agreement** → Creates embeddings, generates initial summary, creates chat session
2. **Ask "summary"** → Generates detailed 600-700 word summary
3. **Ask questions** → Get AI responses about the agreement
4. **Chat naming** → Automatic AI-generated names like "Employment Contract Review"

## For Node.js Integration

See `API_DOCUMENTATION.md` for detailed API documentation and JavaScript examples.