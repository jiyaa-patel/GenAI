from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import ChatSession, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_chat_session(request, chat_session_id):
    """Debug endpoint to check chat session existence"""
    try:
        # Check if session exists at all
        session_exists = ChatSession.objects.filter(id=chat_session_id).exists()
        
        # Check if session exists for current user
        user_session_exists = ChatSession.objects.filter(id=chat_session_id, user=request.user).exists()
        
        # Get all sessions for current user
        user_sessions = list(ChatSession.objects.filter(user=request.user).values('id', 'name', 'user_id'))
        
        # Get messages count for this session
        message_count = ChatMessage.objects.filter(chat_session_id=chat_session_id).count()
        
        return Response({
            'session_id': str(chat_session_id),
            'session_exists_globally': session_exists,
            'session_exists_for_user': user_session_exists,
            'current_user_id': request.user.id,
            'current_user_email': request.user.email,
            'user_sessions': user_sessions,
            'message_count_for_session': message_count
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)