#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from geniai.django_sync import DjangoSync
from users.models import User
import uuid

print("=== Testing Django Sync ===")

# Get a test user
try:
    user = User.objects.order_by('-id').first()
    if not user:
        print("No users found in database")
        exit(1)
    
    print(f"Using user: {user.email}")
    
    # Test DjangoSync
    sync = DjangoSync(user_email=user.email)
    
    # Test message creation
    test_session_id = str(uuid.uuid4())
    test_doc_id = str(uuid.uuid4())
    
    # Create test session
    result = sync.create_chat_session(test_session_id, "Test Sync Session", test_doc_id)
    print(f"Session creation: {result}")
    
    # Create test message
    result = sync.create_chat_message(test_session_id, "user", "Test message from sync test")
    print(f"Message creation: {result}")
    
    # Create AI response
    result = sync.create_chat_message(test_session_id, "assistant", "Test AI response from sync test")
    print(f"AI message creation: {result}")
    
    print("Django sync test completed successfully!")
    
except Exception as e:
    print(f"Django sync test failed: {e}")
    import traceback
    traceback.print_exc()