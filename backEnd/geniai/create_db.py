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
from pathlib import Path

load_dotenv()

# Set up Google Cloud authentication
def setup_authentication():
    """Set up Google Cloud authentication using service account credentials."""
    # Get the directory of the current script
    script_dir = Path(__file__).parent
    credentials_path = script_dir.parent / "credentials" / "gen-ai-legal-536c695ad0a1.json"
    
    # Set GOOGLE_APPLICATION_CREDENTIALS if not set and credentials file exists
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and credentials_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
        print(f"✓ GOOGLE_APPLICATION_CREDENTIALS set to {credentials_path}")
    elif not credentials_path.exists():
        print(f"⚠ Warning: Credentials file not found at {credentials_path}")
        print("Please ensure the service account JSON file is in the correct location.")
    
    # Set project ID
    os.environ.setdefault("GCP_PROJECT", os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-ai-legal"))

# Initialize authentication
setup_authentication()

# Vertex AI is used only for embeddings
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-ai-legal"
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")


def ensure_dirs():
    if not os.path.exists(VECTOR_DIR):
        os.makedirs(VECTOR_DIR, exist_ok=True)


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


def save_index_and_chunks(index, chunks):
    ensure_dirs()
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    print(f"Saved FAISS index to: {INDEX_PATH}")
    print(f"Saved chunks to: {CHUNKS_PATH}")


if __name__ == "__main__":
    import sys

    # Determine input PDF
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(script_dir, "data", "perfect commercial lease.pdf")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        print("Usage: python create_db.py path/to/document.pdf")
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
        
        # Save summary to a separate file
        summary_file = os.path.join(os.path.dirname(pdf_path), f"{os.path.splitext(os.path.basename(pdf_path))[0]}_summary.txt")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Agreement Type: {summary_result['agreement_type']}\n")
            f.write(f"Summary Length: {summary_result['word_count']} words\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*50 + "\n")
            f.write(summary_result['summary'])
            f.write("\n" + "="*50 + "\n")
        
        print(f"\nSummary saved to: {summary_file}")
        
        # Generate and save chat session
        try:
            chat_name = generate_chat_name(
                document_name=os.path.basename(pdf_path),
                document_summary=summary_result['summary']
            )
            chat_id = int(time.time() * 1000)  # Use timestamp as unique ID
            save_chat_session(
                chat_id=chat_id,
                chat_name=chat_name,
                document_name=os.path.basename(pdf_path),
                document_path=pdf_path
            )
            print(f"Chat session created: '{chat_name}' (ID: {chat_id})")
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

    print("Saving index and chunks to disk...")
    save_index_and_chunks(index, chunks)
    print("Done. You can now run query.py to ask questions.")
