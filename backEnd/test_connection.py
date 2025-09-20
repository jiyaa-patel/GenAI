import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from django.db import connection
from geniai.models import Document, ChatSession, ChatMessage
from users.models import User

print("Database Connection Test")
print("=" * 30)

# Test connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"Connected to: {result[0]}")
        
        # Test table counts
        print(f"\nTable Counts:")
        print(f"Users: {User.objects.count()}")
        print(f"Documents: {Document.objects.count()}")
        print(f"Chat Sessions: {ChatSession.objects.count()}")
        print(f"Chat Messages: {ChatMessage.objects.count()}")
        
        # Show recent records
        print(f"\nRecent Documents:")
        for doc in Document.objects.order_by('-created_at')[:3]:
            print(f"- {doc.original_filename} by {doc.user.email}")
            
        print(f"\nRecent Chat Sessions:")
        for session in ChatSession.objects.order_by('-created_at')[:3]:
            print(f"- {session.name} by {session.user.email}")
            
except Exception as e:
    print(f"Connection failed: {e}")