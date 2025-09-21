from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import time
import uuid
import faiss
import numpy as np
from datetime import datetime

# Import our existing modules
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
    build_faiss_index, 
    save_index_and_chunks,
    ensure_dirs
)
from query import (
    load_index_and_chunks,
    embed_query,
    search,
    load_gemini_model
)

app = FastAPI(
    title="Legal Agreement Analyzer API",
    description="API for analyzing legal agreements with AI-powered chat functionality",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatNameRequest(BaseModel):
    document_name: str
    document_summary: Optional[str] = None
    first_query: Optional[str] = None

class ChatSessionRequest(BaseModel):
    chat_id: Optional[str] = None
    chat_name: str
    document_name: str
    document_path: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None
    document_id: Optional[str] = None  # Add document_id to link queries to specific documents

class ChatSessionUpdateRequest(BaseModel):
    chat_id: str
    updates: dict

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

class ChatMessage(BaseModel):
    id: str
    message_type: str  # 'user' or 'assistant'
    content: str
    created_at: str

class ChatHistoryResponse(BaseModel):
    success: bool
    messages: List[ChatMessage]
    chat_id: str

class ChatSession(BaseModel):
    id: str
    name: str
    document_name: str
    document_path: Optional[str] = None
    created_at: str
    last_updated: str
    message_count: int

# Global variables for current session
current_chat_id = None
current_document_id = None

# Chat messages storage
CHAT_MESSAGES_FILE = "data/chat_messages.json"

def load_chat_messages():
    """Load chat messages from file."""
    if os.path.exists(CHAT_MESSAGES_FILE):
        with open(CHAT_MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_chat_messages(messages):
    """Save chat messages to file."""
    os.makedirs(os.path.dirname(CHAT_MESSAGES_FILE), exist_ok=True)
    with open(CHAT_MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def save_chat_message(chat_id: str, message_type: str, content: str):
    """Save a single chat message."""
    messages = load_chat_messages()
    if chat_id not in messages:
        messages[chat_id] = []
    
    message = {
        "id": str(uuid.uuid4()),
        "message_type": message_type,
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    
    messages[chat_id].append(message)
    save_chat_messages(messages)
    return message

def get_chat_messages(chat_id: str) -> List[dict]:
    """Get all messages for a chat session."""
    messages = load_chat_messages()
    return messages.get(chat_id, [])

def check_document_uploaded(document_id: str) -> bool:
    """Check if a document has been uploaded and processed."""
    if not document_id:
        return False
    
    vector_dir = f"data/vectorstore_{document_id}"
    index_path = os.path.join(vector_dir, "index.faiss")
    chunks_path = os.path.join(vector_dir, "chunks.json")
    
    return os.path.exists(index_path) and os.path.exists(chunks_path)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Agreement Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload_document": "POST /api/upload-document",
            "generate_chat_name": "POST /api/generate-chat-name",
            "ask_question": "POST /api/ask-question",
            "get_chat_sessions": "GET /api/chat-sessions",
            "get_chat_history": "GET /api/chat-history/{chat_id}",
            "update_chat_session": "POST /api/update-chat-session",
            "health": "GET /api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a legal document PDF.
    Creates embeddings, builds search index, and generates a chat session.
    """
    global current_chat_id, current_document_id
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique IDs
        document_id = str(uuid.uuid4())
        chat_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{document_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        print(f"Processing document: {file.filename}")
        text = load_pdf(file_path)
        print(f"Loaded PDF with {len(text)} characters")
        
        # Split into chunks
        chunks = split_text(text, chunk_size=1200, overlap=200)
        print(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = get_embeddings(chunks, batch_size=32)
        print(f"Got embeddings for {len(embeddings)} chunks")
        
        # Build FAISS index
        print("Building FAISS index...")
        index = build_faiss_index(embeddings)
        
        # Save index and chunks
        vector_dir = f"data/vectorstore_{document_id}"
        os.makedirs(vector_dir, exist_ok=True)
        index_path = os.path.join(vector_dir, "index.faiss")
        chunks_path = os.path.join(vector_dir, "chunks.json")
        
        faiss.write_index(index, index_path)
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False)
        
        # Generate initial summary and chat name
        chat_name = None
        initial_summary = None
        try:
            analyzer = AgreementAnalyzer()
            summary_text = " ".join(chunks[:5])  # Use first 5 chunks for summary
            summary_result = analyzer.generate_summary(summary_text)
            
            # Store the initial summary
            initial_summary = {
                "agreement_type": summary_result['agreement_type'],
                "word_count": summary_result['word_count'],
                "summary": summary_result['summary']
            }
            
            # Generate chat name based on document and summary
            chat_name = generate_chat_name(
                document_name=file.filename,
                document_summary=summary_result['summary']
            )
            
            # Save initial summary
            summary_file = os.path.join(upload_dir, f"{document_id}_summary.txt")
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"Agreement Type: {summary_result['agreement_type']}\n")
                f.write(f"Summary Length: {summary_result['word_count']} words\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n")
                f.write(summary_result['summary'])
                f.write("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"Warning: Could not generate initial summary: {e}")
            # Fallback chat name
            chat_name = generate_chat_name(document_name=file.filename)
        
        # Save chat session
        save_chat_session(
            chat_id=chat_id,
            chat_name=chat_name,
            document_name=file.filename,
            document_path=file_path
        )
        
        # Update global variables
        current_chat_id = chat_id
        current_document_id = document_id
        
        return DocumentUploadResponse(
            success=True,
            message=f"Document '{file.filename}' processed successfully. You can now start chatting!",
            chat_id=chat_id,
            chat_name=chat_name,
            document_id=document_id,
            initial_summary=initial_summary
        )
        
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/generate-chat-name")
async def generate_chat_name_endpoint(request: ChatNameRequest):
    """Generate a chat name based on document information."""
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
        
        return {
            "success": True,
            "chat_name": chat_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat name: {str(e)}")

@app.post("/api/ask-question", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question about the uploaded legal document.
    Users can only chat after uploading a document and getting a response from Vertex AI.
    """
    global current_chat_id, current_document_id
    
    try:
        # Check if document is uploaded and processed
        document_id = request.document_id or current_document_id
        
        if not document_id:
            raise HTTPException(
                status_code=400, 
                detail="No document uploaded. Please upload a document first to start chatting."
            )
        
        if not check_document_uploaded(document_id):
            raise HTTPException(
                status_code=400, 
                detail="Document not processed yet. Please wait for document processing to complete before asking questions."
            )
        
        # Load the document's index and chunks
        vector_dir = f"data/vectorstore_{document_id}"
        index_path = os.path.join(vector_dir, "index.faiss")
        chunks_path = os.path.join(vector_dir, "chunks.json")
        
        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            raise HTTPException(status_code=404, detail="Document index not found. Please re-upload the document.")
        
        # Load index and chunks
        index = faiss.read_index(index_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        # Get or create chat session
        chat_id = request.chat_id or current_chat_id
        
        if not chat_id:
            # Create new chat session for this document
            chat_id = str(uuid.uuid4())
            chat_name = generate_chat_name_from_query(
                document_name="Legal Document",
                query=request.query
            )
            save_chat_session(
                chat_id=chat_id,
                chat_name=chat_name,
                document_name="Legal Document"
            )
            current_chat_id = chat_id
        
        # Save user message
        save_chat_message(chat_id, "user", request.query)
        
        # Handle special "summary" command
        if request.query.lower() == "summary":
            # Generate detailed summary using AgreementAnalyzer
            try:
                analyzer = AgreementAnalyzer()
                summary_text = " ".join(chunks[:5])  # Use first 5 chunks for summary
                summary_result = analyzer.generate_detailed_summary(summary_text)
                
                response_text = f"Agreement Type: {summary_result['agreement_type']}\n"
                response_text += f"Summary Length: {summary_result['word_count']} words\n\n"
                response_text += "DETAILED SUMMARY:\n"
                response_text += "=" * 60 + "\n"
                response_text += summary_result['summary']
                response_text += "\n" + "=" * 60
                
                # Save assistant response
                save_chat_message(chat_id, "assistant", response_text)
                
                return QueryResponse(
                    success=True,
                    response=response_text,
                    chat_id=chat_id,
                    message_count=len(get_chat_messages(chat_id))
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error generating detailed summary: {str(e)}")
        
        # Load Gemini model for regular queries
        model = load_gemini_model()
        
        # Embed query and search
        q_vec = embed_query(request.query)
        top_idx = search(index, q_vec, k=3)
        context = [chunks[i] for i in top_idx]
        
        # Build prompt for legal analysis
        prompt = f"""You are a professional legal assistant who explains complex legal documents in simple, easy-to-understand language for people without legal backgrounds.

CONTEXT FROM DOCUMENT:
{"\n\n".join(context)}

USER QUESTION: {request.query}

INSTRUCTIONS:
- **Use simple language** - Explain legal terms in plain English that anyone can understand
- **Break down complexity** - Take complex legal concepts and make them clear and accessible
- **Provide practical understanding** - Help users grasp what the legal language actually means for them
- **Maintain professionalism** - Be helpful and informative while staying professional
- **Give detailed answers when needed** - If the question requires steps, procedures, or comprehensive explanation, provide them

RESPONSE STYLE:
- Start with a clear, direct answer to the question
- **If the question requires detailed steps or procedures, provide them clearly**
- **Use bullet points and numbered lists when they make complex information easier to understand**
- Break down complex legal concepts into simple, understandable parts
- Use examples and practical explanations when helpful
- Avoid legal jargon and complex terminology
- Be informative and helpful without being overly casual
- **Adapt response length to the complexity of the question**

Remember: Your goal is to make legal documents understandable for non-legal professionals. Use clear, simple language while maintaining professional credibility. If a question needs detailed steps or comprehensive explanation, provide it."""

        # Generate response
        resp = model.generate_content(prompt)
        response_text = getattr(resp, 'text', str(resp))
        
        # Save assistant response
        save_chat_message(chat_id, "assistant", response_text)
        
        # Update chat session
        try:
            sessions = load_chat_sessions()
            for session in sessions:
                if session["id"] == chat_id:
                    session["message_count"] = len(get_chat_messages(chat_id))
                    session["last_updated"] = datetime.now().isoformat()
                    break
            
            # Save updated sessions
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            sessions_file = os.path.join(data_dir, "chat_sessions.json")
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not update chat session: {e}")
        
        return QueryResponse(
            success=True,
            response=response_text,
            chat_id=chat_id,
            message_count=len(get_chat_messages(chat_id))
        )
        
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/api/chat-sessions", response_model=List[ChatSession])
async def get_chat_sessions():
    """Get all chat sessions."""
    try:
        sessions = load_chat_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat sessions: {str(e)}")

@app.get("/api/chat-history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str):
    """Get chat history for a specific chat session."""
    try:
        messages = get_chat_messages(chat_id)
        return ChatHistoryResponse(
            success=True,
            messages=[ChatMessage(**msg) for msg in messages],
            chat_id=chat_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat history: {str(e)}")

@app.post("/api/update-chat-session")
async def update_chat_session_endpoint(request: ChatSessionUpdateRequest):
    """Update an existing chat session."""
    try:
        success = update_chat_session(request.chat_id, request.updates)
        if success:
            return {"success": True, "message": "Chat session updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update chat session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat session: {str(e)}")

@app.post("/api/save-chat-session")
async def save_chat_session_endpoint(request: ChatSessionRequest):
    """Save a new chat session."""
    try:
        chat_id = request.chat_id or str(uuid.uuid4())
        save_chat_session(
            chat_id=chat_id,
            chat_name=request.chat_name,
            document_name=request.document_name,
            document_path=request.document_path
        )
        return {
            "success": True,
            "message": "Chat session saved successfully",
            "chat_id": chat_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving chat session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting Legal Agreement Analyzer API...")
    print("API Documentation available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
