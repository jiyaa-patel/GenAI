#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from django_sync import DjangoSync
import uuid

# Test the sync functionality
sync = DjangoSync()

# Test creating a document
doc_id = str(uuid.uuid4())
print(f"Testing document creation with ID: {doc_id}")
result = sync.create_document(doc_id, "test_document.pdf")
print(f"Document creation result: {result}")

# Test creating a chat session
chat_id = str(uuid.uuid4())
print(f"Testing chat session creation with ID: {chat_id}")
result = sync.create_chat_session(chat_id, "Test Chat", doc_id)
print(f"Chat session creation result: {result}")

# Test creating a chat message
print(f"Testing chat message creation")
result = sync.create_chat_message(chat_id, "user", "Hello, this is a test message")
print(f"Chat message creation result: {result}")

# Check database
from geniai.models import Document, ChatSession, ChatMessage
print(f"\nDatabase status after sync:")
print(f"Documents: {Document.objects.count()}")
print(f"Chat Sessions: {ChatSession.objects.count()}")
print(f"Chat Messages: {ChatMessage.objects.count()}")