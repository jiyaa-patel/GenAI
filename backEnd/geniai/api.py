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
from fastapi import Request
from asgiref.sync import sync_to_async

# Setup Django before importing DjangoSync
import sys
from pathlib import Path

# Add parent directory to Python path for Django imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Set GCS credentials
creds_path = os.path.join(parent_dir, "credentials", "gen-ai-legal-536c695ad0a1.json")
if os.path.exists(creds_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
    print(f"Set GCS credentials: {creds_path}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
import django
django.setup()

from geniai.django_sync import DjangoSync

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
    build_faiss_index
)
from query import (
    load_index_and_chunks,
    embed_query,
    search,
    load_gemini_model
)
import requests as http

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

class GoogleLoginRequest(BaseModel):
    token: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None

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

async def check_document_uploaded(document_id: str) -> bool:
    """Check if a document has been uploaded and processed in GCS."""
    if not document_id:
        return False
    
    try:
        from geniai.models import Document
        doc = await sync_to_async(Document.objects.get)(id=document_id)
        return bool(doc.gcs_vector_uri and doc.gcs_chunks_uri)
    except:
        return False

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Agreement Analyzer API - DEBUG VERSION",
        "version": "1.0.0-DEBUG",
        "debug": "This is the version with debug logging",
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

@app.post("/api/google-login", response_model=LoginResponse)
async def google_login(request: GoogleLoginRequest):
    """Handle Google OAuth login."""
    try:
        # Verify Google token
        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
        response = http.get(google_verify_url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        user_info = response.json()
        
        # Extract user information
        email = user_info.get('email')
        user_id = user_info.get('sub')
        
        if not email or not user_id:
            raise HTTPException(status_code=400, detail="Invalid token data")
        
        # Here you can add user to database or session management
        # For now, just return success
        
        return LoginResponse(
            success=True,
            message="Login successful",
            user_id=user_id,
            email=email
        )
        
    except Exception as e:
        print(f"Google login error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")

@app.post("/api/upload-document", response_model=DocumentUploadResponse)
async def upload_document(request: Request, file: UploadFile = File(...)):
    print(f"\n=== UPLOAD DOCUMENT CALLED ===")
    print(f"File: {file.filename}")
    print(f"Content Type: {file.content_type}")
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
        
        # Extract user email from request first
        user_email = request.headers.get('x-user-email')
        auth_header = request.headers.get('authorization')
        
        print(f"=== UPLOAD DEBUG ===")
        print(f"x-user-email header: {user_email}")
        print(f"authorization header: {auth_header}")
        print(f"All headers: {dict(request.headers)}")
        
        # If no user email, try to get from any authenticated user for now
        if not user_email:
            print("Warning: No user email in headers, using fallback")
            try:
                from users.models import User
                recent_user = await sync_to_async(User.objects.order_by('-id').first)()
                if recent_user:
                    user_email = recent_user.email
                    print(f"Using recent user email: {user_email}")
            except Exception as e:
                print(f"Fallback user lookup failed: {e}")
        
        # Save to GCS (required)
        from create_db import save_index_and_chunks_to_gcs
        gcs_user_id = user_email.replace('@', '_').replace('.', '_') if user_email else 'anonymous'
        
        print(f"Saving to GCS for user: {gcs_user_id}")
        gcs_index_path, gcs_chunks_path = save_index_and_chunks_to_gcs(index, chunks, gcs_user_id, document_id)
        print(f"Successfully saved to GCS: {gcs_index_path}, {gcs_chunks_path}")
        
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

        print(f"Final user email for Django sync: {user_email}")
        
        # Sync to Django database with user context (wrapped in sync_to_async)
        try:
            if not user_email:
                print("Warning: No user email found, skipping Django sync")
                raise Exception("No user email for Django sync")
            
            # Create DjangoSync in sync context
            django_sync = await sync_to_async(DjangoSync)(auth_header=auth_header, user_email=user_email)
            
            # Upload PDF to GCS (required)
            from google.cloud import storage
            storage_client = storage.Client()
            bucket_name = os.getenv("GCS_BUCKET_NAME", "legal-agreement-analyzer-gen-ai-legal")
            bucket = storage_client.bucket(bucket_name)
            
            # Upload PDF to GCS
            pdf_blob_path = f"users/{gcs_user_id}/documents/{document_id}/{file.filename}"
            pdf_blob = bucket.blob(pdf_blob_path)
            
            print(f"Uploading PDF to GCS: gs://{bucket_name}/{pdf_blob_path}")
            with open(file_path, "rb") as f:
                pdf_blob.upload_from_file(f)
            
            gcs_pdf_uri = f"gs://{bucket_name}/{pdf_blob_path}"
            gcs_vector_uri = f"gs://{bucket_name}/{gcs_index_path}"
            gcs_chunks_uri_full = f"gs://{bucket_name}/{gcs_chunks_path}"
            
            print(f"Successfully uploaded to GCS:")
            print(f"  PDF: {gcs_pdf_uri}")
            print(f"  Vector: {gcs_vector_uri}")
            print(f"  Chunks: {gcs_chunks_uri_full}")
            
            # Create Document in Django
            doc_created = await sync_to_async(django_sync.create_document)(
                document_id=document_id,
                filename=file.filename,
                content_type=file.content_type or "application/pdf",
                gcs_pdf_uri=gcs_pdf_uri,
                gcs_vector_uri=gcs_vector_uri,
                gcs_chunks_uri=gcs_chunks_uri_full
            )
            print(f"Document created in Django: {doc_created}")
            
            # Create Chat Session in Django
            chat_created = await sync_to_async(django_sync.create_chat_session)(
                chat_id=chat_id,
                name=chat_name or "New Chat",
                document_id=document_id
            )
            print(f"Chat session created in Django: {chat_created}")
            
            # Create Summary in GCS and Django
            if initial_summary:
                # Save summary to GCS
                from create_db import save_summary_to_gcs
                gcs_summary_path = save_summary_to_gcs(initial_summary, gcs_user_id, document_id)
                print(f"Summary saved to GCS: gs://{bucket_name}/{gcs_summary_path}")
                
                # Save summary to Django
                summary_created = await sync_to_async(django_sync.create_summary)(document_id, initial_summary)
                print(f"Summary created in Django: {summary_created}")
        except Exception as django_error:
            print(f"WARNING: Django sync failed: {django_error}")
            import traceback
            traceback.print_exc()
            # Continue without Django sync - the FastAPI functionality will still work

        
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
    print(f"\n=== ASK QUESTION CALLED ===")
    print(f"Query: {request.query}")
    print(f"Chat ID: {request.chat_id}")
    print(f"Document ID: {request.document_id}")
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
        
        if not await check_document_uploaded(document_id):
            raise HTTPException(
                status_code=400, 
                detail="Document not processed yet. Please wait for document processing to complete before asking questions."
            )
        
        # Load the document's index and chunks from GCS
        from geniai.models import Document
        doc = await sync_to_async(Document.objects.get)(id=document_id)
        
        if not doc.gcs_vector_uri or not doc.gcs_chunks_uri:
            raise HTTPException(status_code=404, detail="Document vectors not found in GCS.")
        
        # Load from GCS
        from google.cloud import storage
        import tempfile
        import io
        storage_client = storage.Client()
        
        print(f"Loading from GCS: {doc.gcs_vector_uri}")
        
        # Download FAISS index from GCS to memory
        bucket_name = doc.gcs_vector_uri.split('/')[2]
        index_blob_path = '/'.join(doc.gcs_vector_uri.split('/')[3:])
        bucket = storage_client.bucket(bucket_name)
        index_blob = bucket.blob(index_blob_path)
        
        # Download to bytes and save to a writable temp directory
        index_data = index_blob.download_as_bytes()
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_index_path = os.path.join(temp_dir, f"index_{document_id}.faiss")
        
        with open(temp_index_path, "wb") as f:
            f.write(index_data)
        
        index = faiss.read_index(temp_index_path)
        
        # Clean up temp file
        try:
            os.remove(temp_index_path)
        except:
            pass
        
        # Download chunks from GCS
        chunks_blob_path = '/'.join(doc.gcs_chunks_uri.split('/')[3:])
        chunks_blob = bucket.blob(chunks_blob_path)
        chunks_data = chunks_blob.download_as_text()
        chunks = json.loads(chunks_data)
        
        print(f"Successfully loaded from GCS: {len(chunks)} chunks")
        
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
            # Also create in Django
            try:
                # Get user email from headers or use fallback
                user_email = request.headers.get('x-user-email')
                if not user_email:
                    try:
                        from users.models import User
                        recent_user = await sync_to_async(User.objects.order_by('-id').first)()
                        if recent_user:
                            user_email = recent_user.email
                    except Exception:
                        pass
                
                if user_email:
                    auth_header = request.headers.get('authorization')
                    django_sync = await sync_to_async(DjangoSync)(auth_header=auth_header, user_email=user_email)
                    await sync_to_async(django_sync.create_chat_session)(chat_id, chat_name, document_id)
                    print(f"Chat session {chat_id} created in Django")
                else:
                    print("ERROR: No user email found for Django sync")
            except Exception as e:
                print(f"ERROR: Django chat session creation failed: {e}")
                import traceback
                traceback.print_exc()
            current_chat_id = chat_id
        
        # Save user message locally and to Django
        save_chat_message(chat_id, "user", request.query)
        
        try:
            # Get user email from headers or use fallback
            user_email = request.headers.get('x-user-email')
            auth_header = request.headers.get('authorization')
            print(f"=== MESSAGE SYNC DEBUG ===")
            print(f"user_email: {user_email}")
            print(f"auth_header: {auth_header}")
            print(f"chat_id: {chat_id}")
            print(f"query: {request.query}")
            print(f"All headers: {dict(request.headers)}")
            
            if not user_email:
                try:
                    from users.models import User
                    recent_user = await sync_to_async(User.objects.order_by('-id').first)()
                    if recent_user:
                        user_email = recent_user.email
                        print(f"DEBUG: Using fallback user email: {user_email}")
                except Exception:
                    pass
            
            if user_email:
                django_sync = await sync_to_async(DjangoSync)(auth_header=auth_header, user_email=user_email)
                await sync_to_async(django_sync.create_chat_message)(chat_id, "user", request.query)
                print(f"✓ User message saved to Django for chat {chat_id}")
            else:
                print("✗ ERROR: No user email found for Django message sync")
        except Exception as e:
            print(f"✗ ERROR: Django message creation failed: {e}")
            import traceback
            traceback.print_exc()
        
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
                
                # Save assistant response locally and to Django
                save_chat_message(chat_id, "assistant", response_text)
                try:
                    # Get user email for Django sync
                    user_email = request.headers.get('x-user-email')
                    auth_header = request.headers.get('authorization')
                    if not user_email:
                        try:
                            from users.models import User
                            recent_user = await sync_to_async(User.objects.order_by('-id').first)()
                            if recent_user:
                                user_email = recent_user.email
                        except Exception:
                            pass
                    
                    if user_email:
                        django_sync = await sync_to_async(DjangoSync)(auth_header=auth_header, user_email=user_email)
                        await sync_to_async(django_sync.create_chat_message)(chat_id, "assistant", response_text)
                        print(f"Assistant message saved to Django for chat {chat_id}")
                except Exception as e:
                    print(f"ERROR: Django assistant message creation failed: {e}")
                    import traceback
                    traceback.print_exc()
                
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
        
        # Save assistant response locally and to Django
        save_chat_message(chat_id, "assistant", response_text)
        try:
            # Get user email for Django sync
            user_email = request.headers.get('x-user-email')
            auth_header = request.headers.get('authorization')
            if not user_email:
                try:
                    from users.models import User
                    recent_user = await sync_to_async(User.objects.order_by('-id').first)()
                    if recent_user:
                        user_email = recent_user.email
                except Exception:
                    pass
            
            if user_email:
                django_sync = await sync_to_async(DjangoSync)(auth_header=auth_header, user_email=user_email)
                await sync_to_async(django_sync.create_chat_message)(chat_id, "assistant", response_text)
                print(f"Assistant message saved to Django for chat {chat_id}")
            else:
                print(f"ERROR: No user email for Django sync")
        except Exception as e:
            print(f"ERROR: Django assistant message creation failed: {e}")
            import traceback
            traceback.print_exc()
            # Don't let this fail the whole request - but log it clearly
            print(f"CRITICAL: Message sync to database failed - messages will only be stored locally")
            pass
        
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
