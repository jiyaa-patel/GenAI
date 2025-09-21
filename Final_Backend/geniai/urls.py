from django.urls import path
from . import views
from .debug_views import debug_chat_session

urlpatterns = [
    path('documents/', views.api_create_document, name='api_create_document'),
    path('documents/<uuid:document_id>/status/', views.api_update_document_status, name='api_update_document_status'),
    path('summaries/', views.api_create_summary, name='api_create_summary'),
    path('chat-sessions/', views.api_create_chat_session, name='api_create_chat_session'),
    path('chat-messages/', views.api_create_chat_message, name='api_create_chat_message'),
    path('chat-sessions/list/', views.api_list_chat_sessions, name='api_list_chat_sessions'),
    path('chat-sessions/<uuid:chat_session_id>/messages/', views.api_chat_messages, name='api_chat_messages'),
    path('chat-sessions/with-messages/', views.api_list_sessions_with_messages, name='api_list_sessions_with_messages'),
    path('current-user/', views.api_get_current_user, name='api_get_current_user'),
    path('health/', views.api_health, name='api_health'),
    path('test/', views.api_test, name='api_test'),
    path('debug/chat-sessions/<uuid:chat_session_id>/', debug_chat_session, name='debug_chat_session'),
]


