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
from geniai.models import Document, ChatSession, ChatMessage
from users.models import User
import uuid

# Test with different users
user1_email = "user1@test.com"
user2_email = "user2@test.com"

print("=== Testing User-Specific Sync ===")

# Test User 1
print(f"\n--- Testing {user1_email} ---")
sync1 = DjangoSync(user_email=user1_email)

doc1_id = str(uuid.uuid4())
chat1_id = str(uuid.uuid4())

sync1.create_document(doc1_id, "user1_document.pdf")
sync1.create_chat_session(chat1_id, "User 1 Chat", doc1_id)
sync1.create_chat_message(chat1_id, "user", "Hello from user 1")

# Test User 2
print(f"\n--- Testing {user2_email} ---")
sync2 = DjangoSync(user_email=user2_email)

doc2_id = str(uuid.uuid4())
chat2_id = str(uuid.uuid4())

sync2.create_document(doc2_id, "user2_document.pdf")
sync2.create_chat_session(chat2_id, "User 2 Chat", doc2_id)
sync2.create_chat_message(chat2_id, "user", "Hello from user 2")

# Check results
print(f"\n=== Results ===")
user1 = User.objects.get(email=user1_email)
user2 = User.objects.get(email=user2_email)

print(f"User 1 ({user1_email}):")
print(f"  Documents: {Document.objects.filter(user=user1).count()}")
print(f"  Chat Sessions: {ChatSession.objects.filter(user=user1).count()}")
print(f"  Messages: {ChatMessage.objects.filter(user=user1).count()}")

print(f"User 2 ({user2_email}):")
print(f"  Documents: {Document.objects.filter(user=user2).count()}")
print(f"  Chat Sessions: {ChatSession.objects.filter(user=user2).count()}")
print(f"  Messages: {ChatMessage.objects.filter(user=user2).count()}")

print(f"\nTotal in database:")
print(f"  Users: {User.objects.count()}")
print(f"  Documents: {Document.objects.count()}")
print(f"  Chat Sessions: {ChatSession.objects.count()}")
print(f"  Messages: {ChatMessage.objects.count()}")