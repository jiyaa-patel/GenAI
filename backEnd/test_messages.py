#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.models import ChatSession, ChatMessage
from users.models import User

print("=== Testing Message Storage ===")

# Get recent chat sessions
sessions = ChatSession.objects.all().order_by('-created_at')[:5]

for session in sessions:
    messages = ChatMessage.objects.filter(chat_session=session)
    print(f"\nSession: {session.name}")
    print(f"  ID: {session.id}")
    print(f"  User: {session.user.email}")
    print(f"  Message Count (field): {session.message_count}")
    print(f"  Actual Messages: {messages.count()}")
    
    for msg in messages:
        print(f"    - {msg.message_type}: {msg.content[:50]}...")

print(f"\nTotal Sessions: {ChatSession.objects.count()}")
print(f"Total Messages: {ChatMessage.objects.count()}")