import os
import json
import time
import numpy as np
import faiss
from dotenv import load_dotenv
from pypdf import PdfReader
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import re
from agreement_analyzer import AgreementAnalyzer
from chat_naming import generate_chat_name, save_chat_session
from google.cloud import storage
from google.cloud import secretmanager   # ✅ Added Secret Manager
import tempfile

load_dotenv()

# GCP Project and Bucket
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-ai-legal"
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "legal-agreement-analyzer")  # ✅ unified name

# Init VertexAI and GCS
vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()
secret_client = secretmanager.SecretManagerServiceClient()  # ✅ Secret Manager client

def get_secret(secret_id, version="latest"):
    """Fetch secret from GCP Secret Manager."""
    try:
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version}"
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"⚠️ Secret Manager fetch failed for {secret_id}: {e}")
        return None

# -------------------------
# GCS Storage Functions
# -------------------------
def read_pdf_text(pdf_path_or_gsuri):
    if pdf_path_or_gsuri.startswith("gs://"):
        _, _, bucket_name, *blob_parts = pdf_path_or_gsuri.split("/", 3) + [""]
        blob_path = blob_parts[0] if blob_parts else ""
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            blob.download_to_filename(tmp.name)
            return load_pdf(tmp.name)
    else:
        return load_pdf(pdf_path_or_gsuri)

def save_index_and_chunks_to_gcs(index, chunks, user_id, document_id):
    """Save FAISS index and chunks to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    index_path = f"users/{user_id}/vectorstore/{document_id}/index.faiss"
    index_blob = bucket.blob(index_path)

    import os as _os
    fd, temp_path = tempfile.mkstemp(suffix=".faiss")
    _os.close(fd)
    try:
        faiss.write_index(index, temp_path)
        with open(temp_path, "rb") as f:
            index_blob.upload_from_file(f)
    finally:
        try:
            _os.remove(temp_path)
        except Exception:
            pass

    chunks_path = f"users/{user_id}/vectorstore/{document_id}/chunks.json"
    chunks_blob = bucket.blob(chunks_path)
    chunks_blob.upload_from_string(json.dumps(chunks, ensure_ascii=False))

    return index_path, chunks_path

def save_summary_to_gcs(summary_data, user_id, document_id):
    """Save summary to GCS."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    summary_path = f"users/{user_id}/summaries/{document_id}_summary.json"
    summary_blob = bucket.blob(summary_path)
    summary_blob.upload_from_string(json.dumps(summary_data, ensure_ascii=False))
    return summary_path



def batch_list(items, batch_size):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def split_text(text, chunk_size=1200, overlap=200):
    """
    Semantic-aware chunking for legal agreements.
    Splits primarily on section headers, numbered clauses, sub-clauses, and legal connectors.
    Falls back to size-based chunking if needed.
    """
    # Define keywords/phrases to detect legal chunk boundaries
    keywords = [
        "Section", "Article", "ARTICLE", "Clause", "Sub-clause", "Definitions",
        "Whereas", "Provided that", "Notwithstanding", "Unless otherwise",
        "Subject to", "In the event that", "Agreement", "Term", "Termination",
        "Confidentiality", "Liability", "Jurisdiction"
    ]

    # First-level split: section headers, articles, clause numbers
    parts = re.split(
        r'(\n\s*(?:Section|Article|ARTICLE|Clause|Sub-clause)?\s*\d+[\.\d]*[A-Za-z]*[:\.\-]?\s*)', 
        text
    )

    # Combine into logical sections
    logical_chunks = []
    buffer = ""
    for part in parts:
        if re.match(r'(\n\s*(?:Section|Article|ARTICLE|Clause|Sub-clause)?\s*\d+[\.\d]*[A-Za-z]*[:\.\-]?\s*)', part):
            if buffer.strip():
                logical_chunks.append(buffer.strip())
                buffer = ""
            buffer += part
        else:
            buffer += part
    if buffer.strip():
        logical_chunks.append(buffer.strip())

    # Second-level split: by legal connectors and punctuation
    refined_chunks = []
    connector_pattern = r'(?<=;)\s+|(?<=\.)\s+(?=[A-Z])|(?=\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b)'
    for chunk in logical_chunks:
        subparts = re.split(connector_pattern, chunk)
        for sub in subparts:
            if sub.strip():
                refined_chunks.append(sub.strip())

    # Merge small chunks and enforce size limits with overlap
    final_chunks = []
    current = ""
    for chunk in refined_chunks:
        if len(current) + len(chunk) < chunk_size:
            current += " " + chunk
        else:
            final_chunks.append(current.strip())
            if overlap > 0 and final_chunks:
                overlap_text = final_chunks[-1][-overlap:]
                current = overlap_text + " " + chunk
            else:
                current = chunk
    if current.strip():
        final_chunks.append(current.strip())

    return final_chunks


def load_embedding_model():
    return TextEmbeddingModel.from_pretrained("text-embedding-004")


def get_embeddings(chunks, batch_size=32, max_retries=3):
    model = load_embedding_model()
    embeddings = []
    for batch in batch_list(chunks, batch_size):
        for attempt in range(max_retries):
            try:
                emb_list = model.get_embeddings(batch)
                embeddings.extend([e.values for e in emb_list])
                break
            except ResourceExhausted:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
            except GoogleAPIError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
    return np.array(embeddings).astype("float32")


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


# Legacy function removed - use GCS functions instead


if __name__ == "__main__":
    import sys

    # Determine input PDF and user_id
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        user_id = sys.argv[2] if len(sys.argv) > 2 else "default_user"
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(script_dir, "data", "perfect commercial lease.pdf")
        user_id = "default_user"

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        print("Usage: python create_db.py path/to/document.pdf [user_id]")
        sys.exit(1)

    print("Loading PDF document...")
    text = load_pdf(pdf_path)
    print(f"Loaded PDF with {len(text)} characters")

    print("\nSplitting into chunks...")
    chunks = split_text(text, chunk_size=1200, overlap=200)
    print(f"Created {len(chunks)} chunks")

    print("Generating embeddings (this may take a moment)...")
    embeddings = get_embeddings(chunks, batch_size=32)
    print(f"Got embeddings for {len(embeddings)} chunks")

    print("Building FAISS index...")
    index = build_faiss_index(embeddings)
    print("Index built")

    # Generate automatic summary based on agreement type (AFTER processing)
    print("\n" + "="*60)
    print("GENERATING AUTOMATIC AGREEMENT SUMMARY")
    print("="*60)
    
    try:
        analyzer = AgreementAnalyzer()
        # Use the first few processed chunks for better context
        summary_text = " ".join(chunks[:5])  # Use first 5 chunks for summary
        summary_result = analyzer.generate_summary(summary_text)
        
        print(f"\nAgreement Type: {summary_result['agreement_type']}")
        print(f"Summary Length: {summary_result['word_count']} words")
        print("\nSUMMARY:")
        print("-" * 50)
        print(summary_result['summary'])
        print("-" * 50)
        
        # Summary is saved to GCS via save_summary_to_gcs function
        print(f"\nSummary saved to GCS for user: {user_id}")
        
        # Generate and save chat session
        try:
            chat_name = generate_chat_name(
                document_name=os.path.basename(pdf_path),
                document_summary=summary_result['summary']
            )
            chat_id = str(int(time.time() * 1000))  # Use timestamp as unique ID
            document_id = str(int(time.time() * 1000) + 1)  # Generate document ID
            
            # Save to GCS
            index_path, chunks_path = save_index_and_chunks_to_gcs(index, chunks, user_id, document_id)
            save_summary_to_gcs(summary_result, user_id, document_id)
            
            save_chat_session(
                chat_id=chat_id,
                chat_name=chat_name,
                document_name=os.path.basename(pdf_path),
                document_path=pdf_path,
                user_id=user_id
            )
            print(f"Chat session created: '{chat_name}' (ID: {chat_id})")
            print(f"Document saved to GCS for user: {user_id}")
        except Exception as e:
            print(f"Warning: Could not create chat session: {e}")
        
    except Exception as e:
        print(f"Warning: Could not generate summary: {e}")
        print("Continuing with document processing...")
        
        # Still try to create a basic chat session even without summary
        try:
            chat_name = generate_chat_name(document_name=os.path.basename(pdf_path))
            chat_id = int(time.time() * 1000)
            save_chat_session(
                chat_id=chat_id,
                chat_name=chat_name,
                document_name=os.path.basename(pdf_path),
                document_path=pdf_path
            )
            print(f"Basic chat session created: '{chat_name}' (ID: {chat_id})")
        except Exception as e:
            print(f"Warning: Could not create basic chat session: {e}")

    print("Done. Document processed and saved to GCS.")
    print("You can now use the API or query.py to ask questions.")