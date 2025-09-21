# Legal Agreement Analyzer API

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
```

### 3. Start the API
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
# Upload document
curl -X POST "http://localhost:8000/api/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employment_contract.pdf"

# Get detailed summary
curl -X POST "http://localhost:8000/api/ask-question" \
  -H "Content-Type: application/json" \
  -d '{"query": "summary"}'

# Ask questions
curl -X POST "http://localhost:8000/api/ask-question" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key terms?"}'
```

## Workflow

1. **Upload legal agreement** → Creates embeddings, generates initial summary, creates chat session
2. **Ask "summary"** → Generates detailed 600-700 word summary
3. **Ask questions** → Get AI responses about the agreement
4. **Chat naming** → Automatic AI-generated names like "Employment Contract Review"

## For Node.js Integration

See `API_DOCUMENTATION.md` for detailed API documentation and JavaScript examples.