# Legal Agreement Analyzer API Documentation

## Overview
This FastAPI-based service provides endpoints for analyzing legal agreements using AI. It includes document upload, processing, chat functionality, and automatic chat naming.

## Base URL
```
http://localhost:8000
```

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Upload Document
**POST** `/api/upload-document`

Upload and process a legal agreement PDF. This creates embeddings, builds a search index, generates an initial summary, and creates a chat session.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file (legal agreement)

**Response:**
```json
{
  "success": true,
  "message": "Document 'employment_contract.pdf' processed successfully",
  "chat_id": "uuid-string",
  "chat_name": "Employment Contract Review",
  "document_id": "uuid-string"
}
```

**Error Responses:**
- `400`: Only PDF files allowed
- `500`: Document processing error

### 3. Ask Question
**POST** `/api/ask-question`

Ask a question about the uploaded legal agreement or request a detailed summary. Creates a chat session when "summary" command is used.

**Request:**
```json
{
  "query": "What are the key terms of this agreement?",
  "chat_id": "optional-uuid-string"
}
```

**Special Commands:**
- `"summary"` - Generates a detailed 600-700 word summary and creates a chat session

**Response:**
```json
{
  "success": true,
  "response": "Based on the agreement, the key terms include...",
  "chat_id": "uuid-string",
  "message_count": 1
}
```

**Error Responses:**
- `400`: No document uploaded
- `404`: Document index not found
- `500`: Question processing error

### 4. Generate Chat Name
**POST** `/api/generate-chat-name`

Generate a chat name based on document information.

**Request:**
```json
{
  "document_name": "employment_contract.pdf",
  "document_summary": "Optional summary text",
  "first_query": "Optional first question"
}
```

**Response:**
```json
{
  "success": true,
  "chat_name": "Employment Contract Review"
}
```

### 5. Get Chat Sessions
**GET** `/api/chat-sessions`

Retrieve all chat sessions.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "name": "Contract Terms Analysis",
    "document_name": "contract.pdf",
    "document_path": "/path/to/file",
    "created_at": "2024-01-15T10:30:00",
    "last_updated": "2024-01-15T10:35:00",
    "message_count": 5
  }
]
```

### 6. Save Chat Session
**POST** `/api/save-chat-session`

Save a new chat session.

**Request:**
```json
{
  "chat_id": "optional-uuid-string",
  "chat_name": "My Legal Chat",
  "document_name": "contract.pdf",
  "document_path": "/path/to/file"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat session saved successfully",
  "chat_id": "uuid-string"
}
```

### 7. Update Chat Session
**POST** `/api/update-chat-session`

Update an existing chat session.

**Request:**
```json
{
  "chat_id": "uuid-string",
  "updates": {
    "name": "Updated Chat Name",
    "message_count": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat session updated successfully"
}
```

## Usage Flow

### Typical Workflow:

1. **Upload Document**
   ```javascript
   const formData = new FormData();
   formData.append('file', pdfFile);
   
   const response = await fetch('/api/upload-document', {
     method: 'POST',
     body: formData
   });
   const result = await response.json();
   const { chat_id, chat_name, document_id } = result;
   ```

2. **Ask Questions or Get Summary**
   ```javascript
   // Ask a regular question
   const questionResponse = await fetch('/api/ask-question', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       query: "What are the termination clauses?",
       chat_id: chat_id
     })
   });
   const answer = await questionResponse.json();
   
   // Get detailed summary (creates chat session)
   const summaryResponse = await fetch('/api/ask-question', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       query: "summary",
       chat_id: chat_id
     })
   });
   const summary = await summaryResponse.json();
   ```

3. **Manage Chat Sessions**
   ```javascript
   // Get all sessions
   const sessions = await fetch('/api/chat-sessions');
   
   // Update session name
   await fetch('/api/update-chat-session', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       chat_id: chat_id,
       updates: { name: "New Chat Name" }
     })
   });
   ```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

Error responses include a `detail` field with the error message:
```json
{
  "detail": "Error message here"
}
```

## Environment Variables Required

The API requires these environment variables:
- `GEMINI_API_KEY`: Google Generative AI API key
- `GCP_PROJECT`: Google Cloud Project ID
- `GCP_LOCATION`: Google Cloud location (default: us-central1)

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python api.py

# Or with uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes for Node.js Developer

1. **File Upload**: Use `multipart/form-data` for document uploads
2. **Chat Management**: Each document upload creates a new chat session automatically
3. **Session Persistence**: Chat sessions are stored in JSON files in the `data/` directory
4. **AI Responses**: The AI is specifically trained for legal document analysis
5. **Chat Naming**: Names are auto-generated using AI based on document content and queries
6. **CORS**: CORS is enabled for all origins (configure properly for production)

## Example Integration

```javascript
class LegalAnalyzerAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseURL}/api/upload-document`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }

  async askQuestion(query, chatId = null) {
    const response = await fetch(`${this.baseURL}/api/ask-question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, chat_id: chatId })
    });
    
    return await response.json();
  }

  async getChatSessions() {
    const response = await fetch(`${this.baseURL}/api/chat-sessions`);
    return await response.json();
  }
}
```
