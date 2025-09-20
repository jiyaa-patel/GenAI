#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.models import ChatSession, ChatMessage, Document
from users.models import User

print("=== Database Status ===")
print(f"Users: {User.objects.count()}")
print(f"Documents: {Document.objects.count()}")
print(f"Chat Sessions: {ChatSession.objects.count()}")
print(f"Chat Messages: {ChatMessage.objects.count()}")

print("\n=== Recent Chat Sessions ===")
for session in ChatSession.objects.all()[:5]:
    print(f"ID: {session.id}")
    print(f"Name: {session.name}")
    print(f"User: {session.user.email if session.user else 'None'}")
    print(f"Document: {session.document.original_filename if session.document else 'None'}")
    print(f"Messages: {ChatMessage.objects.filter(chat_session=session).count()}")
    print("---")