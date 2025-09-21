import os
from typing import Optional
from geniai.models import Document, ChatSession, ChatMessage, DocumentSummary
from users.models import User

class DjangoSync:
    def __init__(self, base_url: str = None, auth_header: str = None, user_email: str = None):
        self.user = None
        if user_email:
            try:
                # Get existing user from database
                self.user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                print(f"User {user_email} not found in database")
                # Don't create user here - they should be created through proper auth
                raise Exception(f"User {user_email} must be authenticated first")
        else:
            raise Exception("User email required for sync")
    
    def create_document(self, document_id: str, filename: str, content_type: str = "application/pdf", gcs_pdf_uri: str = None, gcs_vector_uri: str = None, gcs_chunks_uri: str = None) -> bool:
        try:
            # Check if document already exists
            if Document.objects.filter(id=document_id).exists():
                print(f"Document {document_id} already exists")
                return True
                
            document = Document(
                id=document_id,
                user=self.user,
                original_filename=filename,
                content_type=content_type,
                gcs_pdf_uri=gcs_pdf_uri,
                gcs_vector_uri=gcs_vector_uri,
                gcs_chunks_uri=gcs_chunks_uri,
                status="ready"
            )
            document.save()
            print(f"Created document: {document_id}")
            return True
        except Exception as e:
            print(f"Failed to create document in Django: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_chat_session(self, chat_id: str, name: str, document_id: str = None) -> bool:
        try:
            # Check if session already exists
            if ChatSession.objects.filter(id=chat_id).exists():
                print(f"Chat session {chat_id} already exists")
                return True
                
            document = None
            if document_id:
                try:
                    document = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    print(f"Document {document_id} not found")
            
            session = ChatSession(
                id=chat_id,
                user=self.user,
                document=document,
                name=name,
                message_count=0
            )
            session.save()
            print(f"Created chat session: {chat_id}")
            return True
        except Exception as e:
            print(f"Failed to create chat session in Django: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_chat_message(self, chat_session_id: str, message_type: str, content: str) -> bool:
        try:
            session = ChatSession.objects.get(id=chat_session_id)
            message = ChatMessage(
                chat_session=session,
                user=session.user,
                message_type=message_type,
                content=content
            )
            message.save()
            
            # Update message count
            session.message_count = ChatMessage.objects.filter(chat_session=session).count()
            session.save()
            print(f"Updated message count to {session.message_count} for session {chat_session_id}")
            
            print(f"Created chat message for session: {chat_session_id}")
            return True
        except Exception as e:
            print(f"Failed to create chat message in Django: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_summary(self, document_id: str, summary_data: dict) -> bool:
        try:
            document = Document.objects.get(id=document_id)
            summary = DocumentSummary(
                document=document,
                user=document.user,
                summary_text=summary_data.get('summary', ''),
                agreement_type=summary_data.get('agreement_type'),
                word_count=summary_data.get('word_count')
            )
            summary.save()
            print(f"Created summary for document: {document_id}")
            return True
        except Exception as e:
            print(f"Failed to create summary in Django: {e}")
            return False