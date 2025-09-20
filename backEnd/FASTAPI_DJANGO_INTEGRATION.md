# FastAPI + Django Integration Guide

## 🔗 Connecting FastAPI with Django Models

### 1. **Setup Django in FastAPI**

Create a new file `geniai/django_setup.py`:

```python
import os
import django
from django.conf import settings

def setup_django():
    """Initialize Django for use in FastAPI"""
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
        django.setup()

# Call this at the start of your FastAPI app
setup_django()
```

### 2. **Update FastAPI Main App**

Modify your `geniai/api.py`:

```python
# Add at the top of api.py
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

# Now import Django models
from geniai.models import Document, DocumentChunk, VectorIndex, ChatSession, ChatMessage, ProcessingJob, DocumentSummary
from users.models import User

# Your existing FastAPI imports...
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
# ... rest of your imports
```

### 3. **Updated API Endpoints**

Replace your existing endpoints with Django-integrated versions:

```python
@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserContext = Depends(get_current_user)
):
    """Upload document and create database records"""
    try:
        # 1. Save file to GCS (your existing logic)
        gcs_uri = await save_file_to_gcs(file, current_user.user_id)
        
        # 2. Create document record in Django
        document = Document.objects.create(
            user_id=current_user.user_id,
            original_filename=file.filename,
            content_type=file.content_type,
            gcs_pdf_uri=gcs_uri,
            status='uploaded'
        )
        
        # 3. Create processing job
        processing_job = ProcessingJob.objects.create(
            document=document,
            status='pending'
        )
        
        # 4. Start background processing (you'll need to implement this)
        # await process_document_async(str(document.id))
        
        return {
            "document_id": str(document.id),
            "job_id": str(processing_job.id),
            "status": "uploaded",
            "message": "Document uploaded successfully. Processing will begin shortly."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/process-document/{document_id}")
async def process_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user)
):
    """Process document: extract text, create chunks, build vector index"""
    try:
        # Get document
        document = Document.objects.get(id=document_id, user_id=current_user.user_id)
        
        # Update status
        document.status = 'processing'
        document.save()
        
        # Get processing job
        processing_job = ProcessingJob.objects.get(document=document)
        processing_job.status = 'processing'
        processing_job.save()
        
        # Extract text from PDF
        text = load_pdf_from_gcs(document.gcs_pdf_uri)
        
        # Split into chunks
        chunks = split_text(text)
        
        # Store chunks in database
        for i, chunk_text in enumerate(chunks):
            DocumentChunk.objects.create(
                document=document,
                chunk_index=i,
                text=chunk_text,
                token_count=len(chunk_text.split())
            )
        
        # Generate embeddings and build FAISS index
        embeddings = get_embeddings(chunks)
        index = build_faiss_index(embeddings)
        
        # Save FAISS index to GCS
        faiss_uri = save_faiss_to_gcs(index, str(document.id))
        chunks_uri = save_chunks_to_gcs(chunks, str(document.id))
        
        # Create vector index record
        VectorIndex.objects.create(
            document=document,
            gcs_faiss_uri=faiss_uri,
            gcs_chunks_uri=chunks_uri
        )
        
        # Update document status
        document.status = 'ready'
        document.save()
        
        # Update processing job
        processing_job.status = 'completed'
        processing_job.completed_at = timezone.now()
        processing_job.save()
        
        return {
            "status": "completed",
            "chunks_count": len(chunks),
            "message": "Document processed successfully"
        }
        
    except Document.DoesNotExist:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        # Update job status to failed
        try:
            processing_job = ProcessingJob.objects.get(document_id=document_id)
            processing_job.status = 'failed'
            processing_job.error_message = str(e)
            processing_job.save()
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/create-chat-session")
async def create_chat_session(
    document_id: str,
    name: Optional[str] = None,
    current_user: UserContext = Depends(get_current_user)
):
    """Create a new chat session for a document"""
    try:
        # Get document
        document = Document.objects.get(id=document_id, user_id=current_user.user_id)
        
        if document.status != 'ready':
            raise HTTPException(
                status_code=400, 
                detail="Document is not ready for chat. Please wait for processing to complete."
            )
        
        # Generate name if not provided
        if not name:
            name = generate_chat_name(document.original_filename)
        
        # Create chat session
        chat_session = ChatSession.objects.create(
            user_id=current_user.user_id,
            document=document,
            name=name
        )
        
        return {
            "chat_session_id": str(chat_session.id),
            "name": chat_session.name,
            "document_name": document.original_filename
        }
        
    except Document.DoesNotExist:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

@app.post("/chat/{chat_session_id}")
async def send_message(
    chat_session_id: str,
    message: str,
    current_user: UserContext = Depends(get_current_user)
):
    """Send a message in a chat session"""
    try:
        # Get chat session
        chat_session = ChatSession.objects.get(
            id=chat_session_id,
            user_id=current_user.user_id
        )
        
        # Store user message
        user_message = ChatMessage.objects.create(
            chat_session=chat_session,
            message_type='user',
            content=message
        )
        
        # Get document and vector index
        document = chat_session.document
        vector_index = document.vector_index
        
        # Load FAISS index from GCS
        index = load_faiss_from_gcs(vector_index.gcs_faiss_uri)
        chunks = load_chunks_from_gcs(vector_index.gcs_chunks_uri)
        
        # Search for relevant chunks
        query_embedding = embed_query(message)
        relevant_chunks = search(index, query_embedding, chunks, top_k=5)
        
        # Generate response using Gemini
        response = generate_response(message, relevant_chunks, chat_session)
        
        # Store assistant message
        assistant_message = ChatMessage.objects.create(
            chat_session=chat_session,
            message_type='assistant',
            content=response
        )
        
        # Update message count
        chat_session.message_count += 2
        chat_session.save()
        
        return {
            "response": response,
            "message_id": str(assistant_message.id)
        }
        
    except ChatSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Chat session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/documents")
async def get_user_documents(
    current_user: UserContext = Depends(get_current_user)
):
    """Get all documents for the current user"""
    try:
        documents = Document.objects.filter(user_id=current_user.user_id).order_by('-created_at')
        
        result = []
        for doc in documents:
            result.append({
                "id": str(doc.id),
                "original_filename": doc.original_filename,
                "status": doc.status,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                "has_summary": hasattr(doc, 'summary'),
                "chunks_count": doc.chunks.count(),
                "chat_sessions_count": doc.chat_sessions.count()
            })
        
        return {"documents": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@app.get("/chat-sessions")
async def get_user_chat_sessions(
    current_user: UserContext = Depends(get_current_user)
):
    """Get all chat sessions for the current user"""
    try:
        chat_sessions = ChatSession.objects.filter(
            user_id=current_user.user_id
        ).order_by('-last_updated')
        
        result = []
        for session in chat_sessions:
            result.append({
                "id": str(session.id),
                "name": session.name,
                "document_name": session.document.original_filename if session.document else None,
                "message_count": session.message_count,
                "created_at": session.created_at.isoformat(),
                "last_updated": session.last_updated.isoformat()
            })
        
        return {"chat_sessions": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat sessions: {str(e)}")

@app.post("/summarize/{document_id}")
async def summarize_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user)
):
    """Generate and store document summary"""
    try:
        # Get document
        document = Document.objects.get(id=document_id, user_id=current_user.user_id)
        
        if document.status != 'ready':
            raise HTTPException(
                status_code=400, 
                detail="Document is not ready for summarization"
            )
        
        # Check if summary already exists
        if hasattr(document, 'summary'):
            return {
                "summary_id": str(document.summary.id),
                "summary": document.summary.summary_text,
                "agreement_type": document.summary.agreement_type,
                "word_count": document.summary.word_count
            }
        
        # Get all chunks
        chunks = DocumentChunk.objects.filter(document=document).order_by('chunk_index')
        full_text = " ".join([chunk.text for chunk in chunks])
        
        # Generate summary
        analyzer = AgreementAnalyzer()
        summary_result = analyzer.generate_summary(full_text)
        
        # Store summary
        summary = DocumentSummary.objects.create(
            document=document,
            summary_text=summary_result['summary'],
            agreement_type=summary_result['agreement_type'],
            word_count=summary_result['word_count']
        )
        
        return {
            "summary_id": str(summary.id),
            "summary": summary_result['summary'],
            "agreement_type": summary_result['agreement_type'],
            "word_count": summary_result['word_count']
        }
        
    except Document.DoesNotExist:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
```

### 4. **Helper Functions**

Add these helper functions to your FastAPI app:

```python
import asyncio
from google.cloud import storage
from datetime import timezone

async def save_file_to_gcs(file: UploadFile, user_id: str) -> str:
    """Save uploaded file to Google Cloud Storage"""
    # Your existing GCS upload logic
    pass

def load_pdf_from_gcs(gcs_uri: str) -> str:
    """Load PDF text from GCS"""
    # Your existing PDF loading logic
    pass

def save_faiss_to_gcs(index, document_id: str) -> str:
    """Save FAISS index to GCS"""
    # Your existing FAISS saving logic
    pass

def save_chunks_to_gcs(chunks: list, document_id: str) -> str:
    """Save chunks to GCS"""
    # Your existing chunks saving logic
    pass

def load_faiss_from_gcs(gcs_uri: str):
    """Load FAISS index from GCS"""
    # Your existing FAISS loading logic
    pass

def load_chunks_from_gcs(gcs_uri: str) -> list:
    """Load chunks from GCS"""
    # Your existing chunks loading logic
    pass

def generate_response(message: str, relevant_chunks: list, chat_session: ChatSession) -> str:
    """Generate AI response using relevant chunks"""
    # Your existing response generation logic
    pass
```

### 5. **Database Connection Management**

For production, you'll want to use connection pooling. Add this to your FastAPI app:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Database connection pool
engine = create_engine(
    "postgresql://postgres:Temp#1234@35.224.143.5:5432/gen_ai_db",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

This integration will give you a complete document management system with proper data persistence in Cloud SQL PostgreSQL!
