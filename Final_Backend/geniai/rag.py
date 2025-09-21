from vertexai.language_models import TextEmbeddingModel
import faiss
import numpy as np
from pypdf import PdfReader
from dotenv import load_dotenv
import os
import vertexai
import time
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import google.generativeai as genai

load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-ai-legal"
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

def load_embedding_model():
    """Load the text embedding model."""
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    return model

def load_chat_model():
    """Load Gemini API chat model using API key only (no Vertex AI)."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY/GOOGLE_API_KEY. Add it to your .env file to use the Gemini API."
        )
    genai.configure(api_key=api_key)
    # Prefer the most available models first
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            # Sanity check
            _ = model.generate_content("ping")
            print(f"Using Gemini API model: {model_name}")
            return model
        except Exception:
            continue
    raise RuntimeError("Failed to initialize any Gemini API model. Check API key and model access.")

def batch_list(items, batch_size):
    """Split items into batches."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def load_pdf(file_path):
    """Load and extract text from PDF."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def split_text(text, chunk_size=1200, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def get_embeddings(chunks, batch_size=5, max_retries=3):
    """Generate embeddings for text chunks."""
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
    """Create FAISS index from embeddings."""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_index(query, index, chunks, embed_model, k=3):
    """Search for similar chunks using FAISS."""
    query_emb = embed_model.get_embeddings([query])[0].values
    query_emb = np.array([query_emb]).astype("float32")
    distances, indices = index.search(query_emb, k)
    return [chunks[i] for i in indices[0]]

def ask_gemini(query, context_chunks):
    """Generate answer using Gemini API with context."""
    model = load_chat_model()
    context = "\n".join(context_chunks)
    
    # Legal document analysis prompt
    legal_analysis_prompt = f"""You are a legal document analyst. Analyze the following legal document sections and identify potential issues, risks, or "sticky points" where clients might get stuck or face problems.

DOCUMENT SECTIONS:
{context}

ANALYSIS REQUEST: {query}

Please provide a comprehensive analysis that includes:

1. **IDENTIFIED RISKS**: List specific clauses, terms, or conditions that could be problematic
2. **CLIENT CONCERNS**: What aspects might confuse or worry a typical client
3. **POTENTIAL CONFLICTS**: Areas where terms might conflict or be unclear
4. **RECOMMENDATIONS**: Suggestions for what clients should pay attention to or negotiate
5. **RED FLAGS**: Any terms that are unusually harsh, one-sided, or potentially unenforceable

Format your response clearly with bullet points and explanations for each identified issue.

ANALYSIS:"""
    
    try:
        response = model.generate_content(legal_analysis_prompt)
        return getattr(response, "text", str(response))
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Error: Unable to generate analysis. Please check your Gemini API configuration."

if __name__ == "__main__":
    try:
        # Load PDF
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(script_dir, "data", "rental1.pdf")
        
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            print("Please ensure your rental agreement PDF is named 'rental1.pdf' and placed in the 'data' folder.")
            exit(1)
            
        print("Loading PDF document...")
        text = load_pdf(pdf_path)
        print(f"Successfully loaded PDF with {len(text)} characters")

        # Split into chunks
        print("Processing document into chunks...")
        chunks = split_text(text, chunk_size=1200, overlap=200)
        print(f"Created {len(chunks)} text chunks")

        # Generate embeddings
        print("Generating embeddings...")
        embeddings = get_embeddings(chunks, batch_size=32)
        print(f"Generated embeddings for {len(embeddings)} chunks")

        # Build FAISS index
        print("Building search index...")
        faiss_index = build_faiss_index(embeddings)
        print("Search index ready")

        # Load embedding model for queries
        print("Loading embedding model...")
        embed_model = load_embedding_model()
        print("Embedding model loaded")

        # Get user query and generate answer
        default_query = "Analyze this legal document and identify all potential issues, risks, and areas where a client might get stuck or face problems."
        query = input(f"Enter your analysis request (or press Enter for default): ").strip()
        if not query:
            query = default_query
        
        print("Searching for relevant document sections...")
        context_chunks = search_index(query, faiss_index, chunks, embed_model)
        print(f"Found {len(context_chunks)} relevant sections")
        
        print("Generating legal analysis...")
        answer = ask_gemini(query, context_chunks)

        print("\n" + "="*50)
        print("LEGAL DOCUMENT ANALYSIS")
        print("="*50)
        print(answer)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env for the Gemini API")
        print("2. Verify the PDF file exists in the data folder")
        print("3. Ensure your API key has access to the specified Gemini model")
        print("\nTo get a Google Generative AI API key:")
        print("- Go to https://makersuite.google.com/app/apikey")
        print("- Create a new API key")
        print("- Add it to your .env file as: GEMINI_API_KEY=your_api_key_here")
