import os
import json
from datetime import datetime
from google.cloud import storage
from typing import List, Dict, Optional

class GCSChatStorage:
    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "legal-agreement-analyzer-gen-ai-legal")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def _get_user_id(self, user_email: str) -> str:
        """Convert email to GCS-safe user ID"""
        return user_email.replace('@', '_').replace('.', '_')
    
    def save_chat_session(self, user_email: str, session_data: Dict) -> bool:
        """Save chat session to GCS"""
        try:
            user_id = self._get_user_id(user_email)
            session_id = session_data['id']
            
            # Path: users/{user}/chat_sessions/{session_id}.json
            blob_path = f"users/{user_id}/chat_sessions/{session_id}.json"
            blob = self.bucket.blob(blob_path)
            
            # Add metadata
            session_data['last_updated'] = datetime.now().isoformat()
            session_data['user_email'] = user_email
            
            blob.upload_from_string(
                json.dumps(session_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            
            print(f"Chat session saved to GCS: gs://{self.bucket_name}/{blob_path}")
            return True
            
        except Exception as e:
            print(f"Failed to save chat session to GCS: {e}")
            return False
    
    def save_chat_message(self, user_email: str, session_id: str, message_data: Dict) -> bool:
        """Save individual message to GCS"""
        try:
            user_id = self._get_user_id(user_email)
            message_id = message_data.get('id', datetime.now().isoformat())
            
            # Path: users/{user}/chat_messages/{session_id}/{message_id}.json
            blob_path = f"users/{user_id}/chat_messages/{session_id}/{message_id}.json"
            blob = self.bucket.blob(blob_path)
            
            # Add metadata
            message_data['session_id'] = session_id
            message_data['user_email'] = user_email
            message_data['created_at'] = message_data.get('created_at', datetime.now().isoformat())
            
            blob.upload_from_string(
                json.dumps(message_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            
            print(f"Message saved to GCS: gs://{self.bucket_name}/{blob_path}")
            return True
            
        except Exception as e:
            print(f"Failed to save message to GCS: {e}")
            return False
    
    def load_chat_sessions(self, user_email: str) -> List[Dict]:
        """Load all chat sessions for a user from GCS"""
        try:
            user_id = self._get_user_id(user_email)
            prefix = f"users/{user_id}/chat_sessions/"
            
            sessions = []
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)
            
            for blob in blobs:
                if blob.name.endswith('.json'):
                    session_data = json.loads(blob.download_as_text())
                    sessions.append(session_data)
            
            # Sort by last_updated
            sessions.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
            return sessions
            
        except Exception as e:
            print(f"Failed to load chat sessions from GCS: {e}")
            return []
    
    def load_chat_messages(self, user_email: str, session_id: str) -> List[Dict]:
        """Load all messages for a session from GCS"""
        try:
            user_id = self._get_user_id(user_email)
            prefix = f"users/{user_id}/chat_messages/{session_id}/"
            
            messages = []
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)
            
            for blob in blobs:
                if blob.name.endswith('.json'):
                    message_data = json.loads(blob.download_as_text())
                    messages.append(message_data)
            
            # Sort by created_at
            messages.sort(key=lambda x: x.get('created_at', ''))
            return messages
            
        except Exception as e:
            print(f"Failed to load chat messages from GCS: {e}")
            return []