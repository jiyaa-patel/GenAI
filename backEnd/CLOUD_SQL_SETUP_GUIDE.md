# Cloud SQL PostgreSQL Setup Guide for GenAI Document Management

## 🗄️ Database Setup Steps

### 1. **Cloud SQL PostgreSQL Instance Setup**

```sql
-- Connect to your Cloud SQL instance and run these commands:

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database (if not exists)
CREATE DATABASE gen_ai_db;

-- Connect to the database
\c gen_ai_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For indexing
```

### 2. **Django Migration to Cloud SQL**

```bash
# In your Django project directory
cd D:\Hackathon\genAi\backEnd

# Apply migrations to Cloud SQL
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser --email admin@yourdomain.com
```

### 3. **Database Schema Overview**

Your Cloud SQL database will have these tables:

```sql
-- Users table (from Django auth)
users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(254) UNIQUE NOT NULL,
  display_name VARCHAR(255),
  password VARCHAR(128),
  is_active BOOLEAN DEFAULT TRUE,
  is_staff BOOLEAN DEFAULT FALSE,
  is_superuser BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);

-- Documents table
documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  original_filename TEXT NOT NULL,
  content_type TEXT,
  gcs_pdf_uri TEXT,
  status VARCHAR(20) DEFAULT 'uploaded',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks
document_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  token_count INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(document_id, chunk_index)
);

-- Vector indexes
vector_indexes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  gcs_faiss_uri TEXT NOT NULL,
  gcs_chunks_uri TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(document_id)
);

-- Chat sessions
chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  message_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Chat messages
chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chat_session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  message_type VARCHAR(10) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔄 Data Flow Process

### **Step 1: User Uploads Document**
```python
# FastAPI endpoint receives file
@app.post("/upload-document")
async def upload_document(file: UploadFile, current_user: UserContext = Depends(get_current_user)):
    # 1. Save file to GCS
    gcs_uri = upload_to_gcs(file, current_user.user_id)
    
    # 2. Create document record in Django
    from geniai.models import Document
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
    
    return {"document_id": str(document.id), "job_id": str(processing_job.id)}
```

### **Step 2: Document Processing**
```python
# Background task processes document
async def process_document(document_id: str):
    document = Document.objects.get(id=document_id)
    
    # Update status to processing
    document.status = 'processing'
    document.save()
    
    # Extract text from PDF
    text = extract_text_from_gcs(document.gcs_pdf_uri)
    
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
    faiss_uri = save_faiss_to_gcs(index, document.id)
    chunks_uri = save_chunks_to_gcs(chunks, document.id)
    
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
    processing_job.save()
```

### **Step 3: Chat Session Creation**
```python
@app.post("/create-chat-session")
async def create_chat_session(
    document_id: str,
    name: Optional[str] = None,
    current_user: UserContext = Depends(get_current_user)
):
    document = Document.objects.get(id=document_id, user=current_user.user_id)
    
    if not name:
        name = generate_chat_name(document.original_filename)
    
    chat_session = ChatSession.objects.create(
        user_id=current_user.user_id,
        document=document,
        name=name
    )
    
    return {"chat_session_id": str(chat_session.id)}
```

### **Step 4: Chat Message Processing**
```python
@app.post("/chat/{chat_session_id}")
async def send_message(
    chat_session_id: str,
    message: str,
    current_user: UserContext = Depends(get_current_user)
):
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
    
    return {"response": response}
```

### **Step 5: Document Summarization**
```python
@app.post("/summarize/{document_id}")
async def summarize_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user)
):
    document = Document.objects.get(id=document_id, user=current_user.user_id)
    
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
    
    return {"summary_id": str(summary.id), "summary": summary_result['summary']}
```

## 🔧 Missing Models to Add

You need to add these models to your `geniai/models.py`:

```python
class ProcessingJob(models.Model):
    """Processing jobs for document analysis"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_default=Func(function='uuid_generate_v4')
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='processing_jobs'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(db_default=Now())
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'processing_jobs'
        ordering = ['-created_at']

class DocumentSummary(models.Model):
    """Document summaries generated by AI"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_default=Func(function='uuid_generate_v4')
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='summary'
    )
    summary_text = models.TextField()
    agreement_type = models.CharField(max_length=100)
    word_count = models.IntegerField()
    created_at = models.DateTimeField(db_default=Now())
    
    class Meta:
        db_table = 'summaries'
        ordering = ['-created_at']
```

## 🚀 Integration Steps

### 1. **Update FastAPI to Use Django Models**
```python
# In your FastAPI app, import Django models
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

# Now you can import Django models
from geniai.models import Document, DocumentChunk, VectorIndex, ChatSession, ChatMessage
from users.models import User
```

### 2. **Environment Variables for Cloud SQL**
```bash
# Add to your .env file
DB_HOST=35.224.143.5
DB_PORT=5432
DB_NAME=gen_ai_db
DB_USER=postgres
DB_PASSWORD=Temp#1234
```

### 3. **GCS Integration**
```python
# Update your GCS functions to use document IDs
def save_faiss_to_gcs(index, document_id):
    bucket_name = "your-bucket-name"
    blob_name = f"users/{document_id}/index.faiss"
    # Upload logic here
    return f"gs://{bucket_name}/{blob_name}"
```

## 📊 Database Performance Optimizations

```sql
-- Add these indexes for better performance
CREATE INDEX CONCURRENTLY idx_documents_user_status ON documents(user_id, status);
CREATE INDEX CONCURRENTLY idx_documents_created_at ON documents(created_at);
CREATE INDEX CONCURRENTLY idx_chunks_document_index ON document_chunks(document_id, chunk_index);
CREATE INDEX CONCURRENTLY idx_chat_sessions_user_updated ON chat_sessions(user_id, last_updated);
CREATE INDEX CONCURRENTLY idx_chat_messages_session_created ON chat_messages(chat_session_id, created_at);

-- Full-text search index for document chunks
CREATE INDEX CONCURRENTLY idx_chunks_text_gin ON document_chunks USING gin(to_tsvector('english', text));
```

## 🔐 Security Considerations

1. **Database Access**: Use Cloud SQL Proxy for secure connections
2. **IAM Roles**: Set up proper IAM roles for GCS access
3. **Connection Pooling**: Use PgBouncer for connection management
4. **Backup Strategy**: Enable automated backups
5. **Monitoring**: Set up Cloud SQL monitoring and alerts

This setup will give you a robust, scalable document management system with proper data persistence in Cloud SQL PostgreSQL!
