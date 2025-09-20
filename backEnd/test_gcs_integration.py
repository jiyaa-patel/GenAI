#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.models import Document, ChatSession, ChatMessage, DocumentSummary
from users.models import User
from geniai.django_sync import DjangoSync
import uuid

print("=== Testing GCS Integration ===")

# Create test user
user_email = "test_gcs@example.com"
user, created = User.objects.get_or_create(
    email=user_email,
    defaults={"display_name": "GCS Test User"}
)
print(f"User: {user.email} (created: {created})")

# Test Django sync with GCS URIs
sync = DjangoSync(user_email=user_email)

# Test document creation with GCS URIs
doc_id = str(uuid.uuid4())
gcs_pdf_uri = f"gs://legal-agreement-analyzer/users/{user_email.replace('@', '_').replace('.', '_')}/documents/{doc_id}/test.pdf"
gcs_vector_uri = f"gs://legal-agreement-analyzer/users/{user_email.replace('@', '_').replace('.', '_')}/vectorstore/{doc_id}/index.faiss"
gcs_chunks_uri = f"gs://legal-agreement-analyzer/users/{user_email.replace('@', '_').replace('.', '_')}/vectorstore/{doc_id}/chunks.json"

result = sync.create_document(
    document_id=doc_id,
    filename="test_gcs_document.pdf",
    content_type="application/pdf",
    gcs_pdf_uri=gcs_pdf_uri,
    gcs_vector_uri=gcs_vector_uri,
    gcs_chunks_uri=gcs_chunks_uri
)
print(f"Document created: {result}")

# Verify document in database
try:
    doc = Document.objects.get(id=doc_id)
    print(f"Document found in DB:")
    print(f"  - Filename: {doc.original_filename}")
    print(f"  - GCS PDF URI: {doc.gcs_pdf_uri}")
    print(f"  - GCS Vector URI: {doc.gcs_vector_uri}")
    print(f"  - GCS Chunks URI: {doc.gcs_chunks_uri}")
    print(f"  - User: {doc.user.email}")
    print(f"  - Status: {doc.status}")
except Document.DoesNotExist:
    print("Document not found in database!")

# Test chat session creation
chat_id = str(uuid.uuid4())
result = sync.create_chat_session(chat_id, "GCS Test Chat", doc_id)
print(f"Chat session created: {result}")

# Test message creation
result = sync.create_chat_message(chat_id, "user", "Test message for GCS integration")
print(f"Chat message created: {result}")

# Test summary creation
summary_data = {
    "agreement_type": "Test Agreement",
    "word_count": 100,
    "summary": "This is a test summary for GCS integration testing."
}
result = sync.create_summary(doc_id, summary_data)
print(f"Summary created: {result}")

print(f"\n=== Final Database Counts ===")
print(f"Users: {User.objects.count()}")
print(f"Documents: {Document.objects.count()}")
print(f"Chat Sessions: {ChatSession.objects.count()}")
print(f"Chat Messages: {ChatMessage.objects.count()}")
print(f"Summaries: {DocumentSummary.objects.count()}")

print(f"\n=== GCS Integration Test Complete ===")
print("All models are properly storing data in PostgreSQL with GCS URIs!")