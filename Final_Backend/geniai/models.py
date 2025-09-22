import uuid
from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class Document(models.Model):
    """
    Documents table - stores file locations in GCS
    """
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        db_column='user_id'
    )
    original_filename = models.TextField()
    content_type = models.TextField(null=True, blank=True)
    gcs_pdf_uri = models.TextField(null=True, blank=True)
    gcs_vector_uri = models.TextField(null=True, blank=True)
    gcs_chunks_uri = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.status})"


class DocumentChunk(models.Model):
    """
    Document chunks table - text for embedding/search
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='document_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_chunks',
        db_column='user_id',
        null=True,
        blank=True
    )
    chunk_index = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    text = models.TextField()
    token_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_chunks'
        unique_together = [['document', 'chunk_index']]
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.original_filename}"


class VectorIndex(models.Model):
    """
    Vector index artifacts table - FAISS stored in GCS
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='vector_index',
        db_column='document_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vector_indexes',
        db_column='user_id',
        null=True,
        blank=True
    )
    gcs_faiss_uri = models.TextField()
    gcs_chunks_uri = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vector_indexes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Vector index for {self.document.original_filename}"


class ChatSession(models.Model):
    """
    Chat sessions table
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        db_column='user_id'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        related_name='chat_sessions',
        null=True,
        blank=True,
        db_column='document_id'
    )
    name = models.TextField()
    message_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['user', 'last_updated']),
            models.Index(fields=['document']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.message_count} messages)"


class ChatMessage(models.Model):
    """
    Chat messages table - stores individual messages in chat sessions
    """
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='chat_session_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        db_column='user_id',
        null=True,
        blank=True
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class ProcessingJob(models.Model):
    """
    Processing jobs table - tracks document processing status
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        db_column='document_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        db_column='user_id',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'processing_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Job for {self.document.original_filename} - {self.status}"


class DocumentSummary(models.Model):
    """
    Document summaries table - stores AI-generated summaries from Vertex AI
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='summary',
        db_column='document_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_summaries',
        db_column='user_id',
        null=True,
        blank=True
    )
    summary_text = models.TextField()
    agreement_type = models.CharField(max_length=100, null=True, blank=True)
    word_count = models.IntegerField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence score for the summary")
    key_points = models.JSONField(null=True, blank=True, help_text="JSON array of key points extracted")
    risk_factors = models.JSONField(null=True, blank=True, help_text="JSON array of identified risk factors")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'summaries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['agreement_type']),
        ]
    
    def __str__(self):
        return f"Summary for {self.document.original_filename} - {self.agreement_type or 'Unknown Type'}"
    
    @property
    def has_key_points(self):
        """Check if key points are available"""
        return bool(self.key_points and len(self.key_points) > 0)
    
    @property
    def has_risk_factors(self):
        """Check if risk factors are available"""
        return bool(self.risk_factors and len(self.risk_factors) > 0)