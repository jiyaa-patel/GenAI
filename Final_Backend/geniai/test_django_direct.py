#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.models import Document, ChatSession, ChatMessage
from users.models import User
import uuid

print("=== Testing Direct Django Model Creation ===")

# Create or get a test user
user, created = User.objects.get_or_create(
    email="test@example.com",
    defaults={"display_name": "Test User"}
)
print(f"User: {user.email} (created: {created})")

# Test creating a document directly
doc_id = str(uuid.uuid4())
try:
    document = Document.objects.create(
        id=doc_id,
        user=user,
        original_filename="test_direct.pdf",
        content_type="application/pdf",
        status="ready"
    )
    print(f"Document created: {document.id}")
except Exception as e:
    print(f"Document creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test creating a chat session directly
chat_id = str(uuid.uuid4())
try:
    session = ChatSession.objects.create(
        id=chat_id,
        user=user,
        document=document,
        name="Test Direct Chat",
        message_count=0
    )
    print(f"Chat session created: {session.id}")
except Exception as e:
    print(f"Chat session creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test creating a message directly
try:
    message = ChatMessage.objects.create(
        chat_session=session,
        user=user,
        message_type="user",
        content="Test direct message"
    )
    print(f"Message created: {message.id}")
except Exception as e:
    print(f"Message creation failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\nFinal counts:")
print(f"Documents: {Document.objects.count()}")
print(f"Chat Sessions: {ChatSession.objects.count()}")
print(f"Messages: {ChatMessage.objects.count()}")