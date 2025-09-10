from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
import faiss
import os
import time
import numpy as np
from datetime import datetime
import tempfile
from google.cloud import storage
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()

# Initialize GCS client
storage_client = storage.Client()

# Configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "legal-agreement-analyzer")
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-ai-legal"


def read_pdf_text(pdf_path_or_gsuri):
    if pdf_path_or_gsuri.startswith("gs://"):
        _, _, bucket_name, *blob_parts = pdf_path_or_gsuri.split("/", 3) + [""]
        blob_path = blob_parts[0] if blob_parts else ""
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            blob.download_to_filename(tmp.name)
            return load_pdf(tmp.name)  # reuse your existing load_pdf
    else:
        return load_pdf(pdf_path_or_gsuri)
        
# Import modules
from chat_naming import (
    generate_chat_name, 
    generate_chat_name_from_query, 
    save_chat_session, 
    load_chat_sessions, 
    update_chat_session
)
from agreement_analyzer import AgreementAnalyzer
from create_db import (
    load_pdf, 
    split_text, 
    get_embeddings, 
    build_faiss_index
)
from query import (
    embed_query,
    search,
    load_gemini_model
)
# Note: Removed unused/nonexistent storage module imports

app = FastAPI(
    title="Legal Agreement Analyzer API",
    description="API for analyzing legal agreements with AI-powered chat functionality",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Pydantic Models
# ---------------------------

class ChatNameRequest(BaseModel):
    document_name: str
    document_summary: Optional[str] = None
    first_query: Optional[str] = None
    user_id: str

class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None
    user_id: str

class ChatSessionUpdateRequest(BaseModel):
    chat_id: str
    updates: dict
    user_id: str

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    chat_id: Optional[str] = None
    chat_name: Optional[str] = None
    document_id: Optional[str] = None
    initial_summary: Optional[dict] = None

class QueryResponse(BaseModel):
    success: bool
    response: str
    chat_id: Optional[str] = None
    message_count: Optional[int] = None

class ChatSession(BaseModel):
    id: str
    name: str
    document_name: str
    document_path: Optional[str] = None
    document_id: Optional[str] = None
    created_at: str
    last_updated: str
    message_count: int

# ---------------------------
# GCS Helper Functions
# ---------------------------

def upload_to_gcs(file_content: bytes, file_path: str, user_id: str) -> str:
    """Upload file to GCS and return the GCS path."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    gcs_path = f"users/{user_id}/documents/{file_path}"
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(file_content)
    return gcs_path

def download_from_gcs(gcs_path: str) -> bytes:
    """Download file from GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    return blob.download_as_bytes()

def save_faiss_index_to_gcs(index, chunks, user_id: str, document_id: str):
    """Save FAISS index and chunks to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    
    # Save FAISS index
    index_path = f"users/{user_id}/vectorstore/{document_id}/index.faiss"
    index_blob = bucket.blob(index_path)
    
    # Create a closed temp file path (Windows-safe) for FAISS write
    import os as _os
    fd, temp_path = tempfile.mkstemp(suffix=".faiss")
    _os.close(fd)
    try:
        faiss.write_index(index, temp_path)
        with open(temp_path, "rb") as f:
            index_blob.upload_from_file(f)
    finally:
        try:
            _os.remove(temp_path)
        except Exception:
            pass
    
    # Save chunks
    chunks_path = f"users/{user_id}/vectorstore/{document_id}/chunks.json"
    chunks_blob = bucket.blob(chunks_path)
    chunks_blob.upload_from_string(json.dumps(chunks, ensure_ascii=False))
    
    return index_path, chunks_path

def load_faiss_index_from_gcs(user_id: str, document_id: str):
    """Load FAISS index and chunks from GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    
    # Load FAISS index
    index_path = f"users/{user_id}/vectorstore/{document_id}/index.faiss"
    index_blob = bucket.blob(index_path)
    
    # Use closed file path for Windows compatibility
    import os as _os
    fd, temp_path = tempfile.mkstemp(suffix=".faiss")
    _os.close(fd)
    try:
        index_blob.download_to_filename(temp_path)
        index = faiss.read_index(temp_path)
    finally:
        try:
            _os.remove(temp_path)
        except Exception:
            pass
    
    # Load chunks
    chunks_path = f"users/{user_id}/vectorstore/{document_id}/chunks.json"
    chunks_blob = bucket.blob(chunks_path)
    chunks_content = chunks_blob.download_as_text()
    chunks = json.loads(chunks_content)
    
    return index, chunks

def save_summary_to_gcs(summary_data: dict, user_id: str, document_id: str):
    """Save summary to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    summary_path = f"users/{user_id}/summaries/{document_id}_summary.json"
    summary_blob = bucket.blob(summary_path)
    summary_blob.upload_from_string(json.dumps(summary_data, ensure_ascii=False))
    return summary_path

def load_summary_from_gcs(user_id: str, document_id: str):
    """Load summary from GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    summary_path = f"users/{user_id}/summaries/{document_id}_summary.json"
    summary_blob = bucket.blob(summary_path)
    summary_content = summary_blob.download_as_text()
    return json.loads(summary_content)

# ---------------------------
# GCS Chat Session Functions
# ---------------------------

def save_chat_session_to_gcs(chat_data: dict, user_id: str):
    """Save chat session to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    chat_path = f"users/{user_id}/chat_sessions/{chat_data['id']}.json"
    chat_blob = bucket.blob(chat_path)
    chat_blob.upload_from_string(json.dumps(chat_data, ensure_ascii=False))
    return chat_path

def load_chat_sessions_from_gcs(user_id: str):
    """Load chat sessions from GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    prefix = f"users/{user_id}/chat_sessions/"
    blobs = bucket.list_blobs(prefix=prefix)
    
    sessions = []
    for blob in blobs:
        if blob.name.endswith('.json'):
            try:
                content = blob.download_as_text()
                session_data = json.loads(content)
                sessions.append(session_data)
            except Exception as e:
                print(f"Error loading chat session {blob.name}: {e}")
    
    return sessions

def update_chat_session_in_gcs(chat_id: str, updates: dict, user_id: str):
    """Update chat session in GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    chat_path = f"users/{user_id}/chat_sessions/{chat_id}.json"
    chat_blob = bucket.blob(chat_path)
    
    try:
        # Load existing data
        existing_content = chat_blob.download_as_text()
        existing_data = json.loads(existing_content)
        
        # Update with new data
        existing_data.update(updates)
        existing_data["last_updated"] = datetime.now().isoformat()
        
        # Save back to GCS
        chat_blob.upload_from_string(json.dumps(existing_data, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"Error updating chat session: {e}")
        return False

# ---------------------------
# Endpoints
# ---------------------------

@app.get("/")
async def root():
    return {
        "message": "Legal Agreement Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload_document": "POST /api/upload-document",
            "generate_chat_name": "POST /api/generate-chat-name",
            "ask_question": "POST /api/ask-question",
            "get_chat_sessions": "GET /api/chat-sessions",
            "update_chat_session": "POST /api/update-chat-session",
            "health": "GET /api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), user_id: str = Form(...)):
    """Upload PDF → store in GCS → build FAISS → create session"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        document_id = str(uuid.uuid4())
        chat_id = str(uuid.uuid4())

        # Read file content and upload to GCS
        content = await file.read()
        gcs_path = upload_to_gcs(content, f"{document_id}_{file.filename}", user_id)
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(content)
            local_path = tmp.name

        # Process PDF
        text = load_pdf(local_path)
        chunks = split_text(text, chunk_size=1200, overlap=200)
        embeddings = get_embeddings(chunks, batch_size=32)
        index = build_faiss_index(embeddings)

        # Save FAISS index and chunks to GCS
        index_path, chunks_path = save_faiss_index_to_gcs(index, chunks, user_id, document_id)

        # Generate initial summary
        analyzer = AgreementAnalyzer()
        summary_text = " ".join(chunks[:5])
        summary_result = analyzer.generate_summary(summary_text)
        initial_summary = {
            "agreement_type": summary_result['agreement_type'],
            "word_count": summary_result['word_count'],
            "summary": summary_result['summary']
        }
        chat_name = generate_chat_name(file.filename, summary_result['summary'])

        # Save summary to GCS
        save_summary_to_gcs(initial_summary, user_id, document_id)
        
        # Save chat session metadata to GCS
        chat_data = {
            "id": chat_id,
            "name": chat_name,
            "document_name": file.filename,
            "document_path": gcs_path,
            "document_id": document_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "message_count": 0
        }
        save_chat_session_to_gcs(chat_data, user_id)

        return DocumentUploadResponse(
            success=True,
            message=f"Document '{file.filename}' processed successfully",
            chat_id=chat_id,
            chat_name=chat_name,
            document_id=document_id,
            initial_summary=initial_summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/generate-chat-name")
async def generate_chat_name_endpoint(request: ChatNameRequest):
    try:
        if request.first_query:
            chat_name = generate_chat_name_from_query(
                document_name=request.document_name,
                query=request.first_query
            )
        else:
            chat_name = generate_chat_name(
                document_name=request.document_name,
                document_summary=request.document_summary,
                first_query=request.first_query
            )
        return {"success": True, "chat_name": chat_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat name: {str(e)}")

@app.post("/api/ask-question", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Answer questions using FAISS index + GCS chunks"""
    try:
        if not request.chat_id:
            raise HTTPException(status_code=400, detail="chat_id is required.")

        # Load chat session from GCS
        sessions = load_chat_sessions_from_gcs(request.user_id)
        session = next((s for s in sessions if s["id"] == request.chat_id), None)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")

        document_id = session.get("document_id")
        if not document_id:
            raise HTTPException(status_code=400, detail="No document linked to this chat.")

        # Load FAISS index and chunks from GCS
        index, chunks = load_faiss_index_from_gcs(request.user_id, document_id)

        # Handle summary request
        if request.query.lower() == "summary":
            analyzer = AgreementAnalyzer()
            summary_text = " ".join(chunks[:5])
            summary_result = analyzer.generate_summary(summary_text)
            response_text = (
                f"Agreement Type: {summary_result['agreement_type']}\n"
                f"Summary Length: {summary_result['word_count']} words\n\n"
                f"{summary_result['summary']}"
            )
        else:
            model = load_gemini_model()
            q_vec = embed_query(request.query)
            top_idx = search(index, q_vec, k=3)
            context = [chunks[i] for i in top_idx]
            prompt = f"""You are a professional legal assistant.

CONTEXT:
{"\n\n".join(context)}

USER QUESTION: {request.query}"""
            resp = model.generate_content(prompt)
            response_text = getattr(resp, 'text', str(resp))

        # Update session
        msg_count = session.get("message_count", 0) + 1
        update_chat_session_in_gcs(request.chat_id, {
            "message_count": msg_count,
            "last_updated": datetime.now().isoformat()
        }, request.user_id)

        return QueryResponse(
            success=True,
            response=response_text,
            chat_id=request.chat_id,
            message_count=msg_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/api/chat-sessions", response_model=List[ChatSession])
async def get_chat_sessions(user_id: str):
    """Get all chat sessions for a user."""
    try:
        return load_chat_sessions_from_gcs(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat sessions: {str(e)}")

@app.post("/api/update-chat-session")
async def update_chat_session_endpoint(request: ChatSessionUpdateRequest):
    try:
        success = update_chat_session_in_gcs(request.chat_id, request.updates, request.user_id)
        if success:
            return {"success": True, "message": "Chat session updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update chat session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat session: {str(e)}")
