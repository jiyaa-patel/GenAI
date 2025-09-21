from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import (
    DocumentSerializer,
    DocumentSummarySerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
)
from .models import Document, ChatSession, ChatMessage


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_document(request):
    """Create a Document record after upload in FastAPI."""
    serializer = DocumentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        document = serializer.save()
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def api_update_document_status(request, document_id):
    try:
        doc = Document.objects.get(id=document_id, user=request.user)
    except Document.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    status_value = request.data.get('status')
    if status_value not in dict(Document.STATUS_CHOICES):
        return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    doc.status = status_value
    doc.save()
    return Response({"id": str(doc.id), "status": doc.status})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_summary(request):
    """Create a DocumentSummary record after AI generates summary in FastAPI."""
    serializer = DocumentSummarySerializer(data=request.data)
    if serializer.is_valid():
        summary = serializer.save()
        return Response(DocumentSummarySerializer(summary).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_chat_session(request):
    serializer = ChatSessionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        sess = serializer.save()
        return Response(ChatSessionSerializer(sess).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_create_chat_message(request):
    serializer = ChatMessageSerializer(data=request.data)
    if serializer.is_valid():
        msg = serializer.save()
        return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_list_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-last_updated')
    data = ChatSessionSerializer(sessions, many=True).data
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def api_chat_messages(request, chat_session_id):
    try:
        sess = ChatSession.objects.get(id=chat_session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({"detail": "Chat session not found for current user"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        messages = ChatMessage.objects.filter(chat_session=sess).order_by('created_at')
        data = ChatMessageSerializer(messages, many=True).data
        return Response(data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['chat_session_id'] = chat_session_id
        serializer = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            msg = serializer.save()
            return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_list_sessions_with_messages(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-last_updated')
    result = []
    for s in sessions:
        messages = ChatMessage.objects.filter(chat_session=s).order_by('created_at')
        result.append({
            'id': str(s.id),
            'name': s.name,
            'message_count': s.message_count,
            'created_at': s.created_at,
            'last_updated': s.last_updated,
            'document_id': str(s.document.id) if s.document_id else None,
            'messages': ChatMessageSerializer(messages, many=True).data,
        })
    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_get_current_user(request):
    """Get current authenticated user info"""
    return Response({
        'id': str(request.user.id),
        'email': request.user.email,
        'display_name': request.user.display_name,
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_test(request):
    """Test endpoint to verify Django server is running"""
    return Response({"message": "Django server is working", "timestamp": str(request.META.get('HTTP_HOST', 'unknown'))})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_health(request):
    """Health check endpoint"""
    return Response({
        "status": "healthy", 
        "user": request.user.email,
        "timestamp": str(request.META.get('HTTP_HOST', 'unknown'))
    })


