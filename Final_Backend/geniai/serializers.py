from rest_framework import serializers
from .models import Document, DocumentSummary, ChatSession, ChatMessage
from users.models import User


class DocumentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'content_type', 'status',
            'gcs_pdf_uri', 'gcs_vector_uri', 'gcs_chunks_uri', 'user', 'user_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'id': {'read_only': False}}

    def create(self, validated_data):
        user_email = validated_data.pop('user_email', None)
        user = self.context.get('request').user if self.context.get('request') else None
        
        # Use authenticated user from request
        if not user or user.is_anonymous:
            raise serializers.ValidationError("User authentication required")
        
        validated_data['user'] = user
        
        # Handle explicit ID if provided
        doc_id = validated_data.pop('id', None)
        document = Document(**validated_data)
        if doc_id:
            document.id = doc_id
        document.save()
        return document


class DocumentSummarySerializer(serializers.ModelSerializer):
    document_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = DocumentSummary
        fields = [
            'id', 'document_id', 'summary_text', 'agreement_type', 'word_count',
            'confidence_score', 'key_points', 'risk_factors', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        from .models import Document
        document_id = validated_data.pop('document_id')
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")
        # Ensure user is set from document
        validated_data['user'] = document.user
        return DocumentSummary.objects.create(document=document, **validated_data)


class ChatSessionSerializer(serializers.ModelSerializer):
    document_id = serializers.UUIDField(write_only=True, required=False)
    id = serializers.UUIDField(required=False)

    class Meta:
        model = ChatSession
        fields = ['id', 'name', 'message_count', 'created_at', 'last_updated', 'document_id']
        read_only_fields = ['message_count', 'created_at', 'last_updated']

    def create(self, validated_data):
        from .models import Document
        request = self.context.get('request')
        user = request.user if request else None
        
        # Use authenticated user from request  
        if not user or user.is_anonymous:
            raise serializers.ValidationError("User authentication required")
        
        document_id = validated_data.pop('document_id', None)
        document = None
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                raise serializers.ValidationError("Document not found")
        
        # Handle explicit ID if provided
        session_id = validated_data.pop('id', None)
        session = ChatSession(user=user, document=document, **validated_data)
        if session_id:
            session.id = session_id
        session.save()
        return session


class ChatMessageSerializer(serializers.ModelSerializer):
    chat_session_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_session_id', 'message_type', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        chat_session_id = validated_data.pop('chat_session_id')
        try:
            chat_session = ChatSession.objects.get(id=chat_session_id)
        except ChatSession.DoesNotExist:
            raise serializers.ValidationError("Chat session not found")
        # Ensure user is set from chat_session
        validated_data['user'] = chat_session.user
        msg = ChatMessage.objects.create(chat_session=chat_session, **validated_data)
        # increment message count
        chat_session.message_count = (chat_session.message_count or 0) + 1
        chat_session.save()
        return msg


