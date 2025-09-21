#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.models import ChatSession, ChatMessage
from users.models import User

# Create the specific session that's being requested
session_id = "eadf8a87-b2c7-481e-a9eb-47acae29d929"
user = User.objects.first()

if user:
    session, created = ChatSession.objects.get_or_create(
        id=session_id,
        defaults={
            'name': 'Test Chat Session',
            'user': user,
            'message_count': 0
        }
    )
    
    if created:
        print(f"Created chat session: {session_id}")
        
        # Add a test message
        ChatMessage.objects.create(
            chat_session=session,
            user=user,
            message_type='user',
            content='Hello, this is a test message'
        )
        
        ChatMessage.objects.create(
            chat_session=session,
            user=user,
            message_type='assistant',
            content='Hello! I am your AI assistant. How can I help you today?'
        )
        
        session.message_count = 2
        session.save()
        
        print("Added test messages")
    else:
        print(f"Session {session_id} already exists")
else:
    print("No users found in database")