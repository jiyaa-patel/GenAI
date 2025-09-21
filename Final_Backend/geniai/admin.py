from django.contrib import admin
from .models import Document, DocumentChunk, VectorIndex, ChatSession, ChatMessage, ProcessingJob, DocumentSummary


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('original_filename', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'original_filename', 'content_type')
        }),
        ('GCS Storage', {
            'fields': ('gcs_pdf_uri',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'token_count', 'created_at')
    list_filter = ('created_at', 'document__status')
    search_fields = ('document__original_filename', 'text')
    readonly_fields = ('id', 'created_at')
    ordering = ('document', 'chunk_index')
    
    fieldsets = (
        (None, {
            'fields': ('id', 'document', 'chunk_index')
        }),
        ('Content', {
            'fields': ('text', 'token_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(VectorIndex)
class VectorIndexAdmin(admin.ModelAdmin):
    list_display = ('document', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__original_filename', 'gcs_faiss_uri')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'document')
        }),
        ('GCS Storage', {
            'fields': ('gcs_faiss_uri', 'gcs_chunks_uri')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'document', 'message_count', 'last_updated')
    list_filter = ('created_at', 'last_updated', 'user')
    search_fields = ('name', 'user__email', 'document__original_filename')
    readonly_fields = ('id', 'created_at', 'last_updated')
    ordering = ('-last_updated',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'document', 'name')
        }),
        ('Statistics', {
            'fields': ('message_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_session', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'chat_session__name')
    readonly_fields = ('id', 'created_at')
    ordering = ('chat_session', 'created_at')
    
    fieldsets = (
        (None, {
            'fields': ('id', 'chat_session', 'message_type')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('document', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('document__original_filename', 'error_message')
    readonly_fields = ('id', 'created_at', 'completed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'document', 'status')
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ('document', 'agreement_type', 'word_count', 'confidence_score', 'created_at')
    list_filter = ('agreement_type', 'created_at')
    search_fields = ('document__original_filename', 'summary_text')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'document', 'agreement_type')
        }),
        ('Summary Content', {
            'fields': ('summary_text', 'word_count', 'confidence_score')
        }),
        ('Analysis Results', {
            'fields': ('key_points', 'risk_factors'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
