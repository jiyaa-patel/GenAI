# Example Usage: Storing Vertex AI Summary Results

## 📝 How to Use DocumentSummary Model with Your Existing Vertex AI Logic

### 1. **Basic Usage - Store Summary Results**

```python
from geniai.models import DocumentSummary, Document

# After your existing Vertex AI summary generation logic
def store_summary_results(document_id, vertex_ai_results):
    """
    Store the results from your existing Vertex AI summary logic
    
    Args:
        document_id: UUID of the document
        vertex_ai_results: Dictionary containing your Vertex AI results
    """
    try:
        document = Document.objects.get(id=document_id)
        
        # Create summary record with your Vertex AI results
        summary = DocumentSummary.objects.create(
            document=document,
            summary_text=vertex_ai_results.get('summary', ''),
            agreement_type=vertex_ai_results.get('agreement_type', ''),
            word_count=vertex_ai_results.get('word_count', 0),
            confidence_score=vertex_ai_results.get('confidence_score'),
            key_points=vertex_ai_results.get('key_points', []),
            risk_factors=vertex_ai_results.get('risk_factors', [])
        )
        
        return summary
        
    except Document.DoesNotExist:
        raise ValueError(f"Document with ID {document_id} not found")
    except Exception as e:
        raise Exception(f"Failed to store summary: {str(e)}")
```

### 2. **Example Integration with Your Existing Code**

```python
# Assuming you have existing Vertex AI logic like this:
def generate_summary_with_vertex_ai(document_text):
    # Your existing Vertex AI logic here
    # This is just an example structure
    return {
        'summary': 'This is a commercial lease agreement...',
        'agreement_type': 'Commercial Lease',
        'word_count': 150,
        'confidence_score': 0.95,
        'key_points': [
            'Lease term: 5 years',
            'Monthly rent: $5,000',
            'Security deposit: $10,000'
        ],
        'risk_factors': [
            'Early termination penalty',
            'Maintenance responsibility unclear'
        ]
    }

# Integration function
def process_document_and_store_summary(document_id):
    """
    Process document and store summary using your existing logic
    """
    # Get document
    document = Document.objects.get(id=document_id)
    
    # Get document text (from your existing logic)
    document_text = get_document_text(document)
    
    # Generate summary using your existing Vertex AI logic
    summary_results = generate_summary_with_vertex_ai(document_text)
    
    # Store results in database
    summary = store_summary_results(document_id, summary_results)
    
    return summary
```

### 3. **API Endpoint Example**

```python
from fastapi import HTTPException
from geniai.models import DocumentSummary

@app.post("/summarize/{document_id}")
async def summarize_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user)
):
    """Generate and store document summary using your existing Vertex AI logic"""
    try:
        # Get document
        document = Document.objects.get(id=document_id, user_id=current_user.user_id)
        
        if document.status != 'ready':
            raise HTTPException(
                status_code=400, 
                detail="Document is not ready for summarization"
            )
        
        # Check if summary already exists
        if hasattr(document, 'summary'):
            return {
                "summary_id": str(document.summary.id),
                "summary": document.summary.summary_text,
                "agreement_type": document.summary.agreement_type,
                "word_count": document.summary.word_count,
                "confidence_score": document.summary.confidence_score,
                "key_points": document.summary.key_points,
                "risk_factors": document.summary.risk_factors
            }
        
        # Use your existing Vertex AI logic here
        # This is where you'd call your existing summary generation function
        vertex_ai_results = your_existing_vertex_ai_function(document)
        
        # Store results
        summary = DocumentSummary.objects.create(
            document=document,
            summary_text=vertex_ai_results.get('summary', ''),
            agreement_type=vertex_ai_results.get('agreement_type', ''),
            word_count=vertex_ai_results.get('word_count', 0),
            confidence_score=vertex_ai_results.get('confidence_score'),
            key_points=vertex_ai_results.get('key_points', []),
            risk_factors=vertex_ai_results.get('risk_factors', [])
        )
        
        return {
            "summary_id": str(summary.id),
            "summary": summary.summary_text,
            "agreement_type": summary.agreement_type,
            "word_count": summary.word_count,
            "confidence_score": summary.confidence_score,
            "key_points": summary.key_points,
            "risk_factors": summary.risk_factors
        }
        
    except Document.DoesNotExist:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
```

### 4. **Query Examples**

```python
# Get all summaries for a user's documents
def get_user_summaries(user_id):
    summaries = DocumentSummary.objects.filter(
        document__user_id=user_id
    ).select_related('document')
    
    return summaries

# Get summary with key points
def get_summary_with_analysis(document_id):
    try:
        summary = DocumentSummary.objects.get(document_id=document_id)
        return {
            'summary': summary.summary_text,
            'has_key_points': summary.has_key_points,
            'has_risk_factors': summary.has_risk_factors,
            'key_points': summary.key_points if summary.has_key_points else [],
            'risk_factors': summary.risk_factors if summary.has_risk_factors else []
        }
    except DocumentSummary.DoesNotExist:
        return None

# Get summaries by agreement type
def get_summaries_by_type(agreement_type):
    return DocumentSummary.objects.filter(
        agreement_type=agreement_type
    ).select_related('document')
```

### 5. **Model Features**

The updated `DocumentSummary` model now includes:

- ✅ **Flexible Fields**: All fields are optional except `summary_text`
- ✅ **JSON Fields**: `key_points` and `risk_factors` can store arrays
- ✅ **Confidence Score**: Store AI confidence level
- ✅ **Helper Properties**: `has_key_points` and `has_risk_factors`
- ✅ **Proper Indexing**: Optimized for queries
- ✅ **Admin Interface**: Complete admin configuration

### 6. **Migration**

Run this to update your database:

```bash
python manage.py makemigrations geniai
python manage.py migrate
```

This model is now perfectly suited to store the results from your existing Vertex AI summary generation logic without any generation logic in the model itself!
