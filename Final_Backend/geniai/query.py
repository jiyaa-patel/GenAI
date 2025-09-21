import os
import json
import time
import numpy as np
import faiss
from dotenv import load_dotenv
import google.generativeai as genai
import vertexai
from vertexai.language_models import TextEmbeddingModel
from agreement_analyzer import AgreementAnalyzer
from chat_naming import generate_chat_name_from_query, save_chat_session, load_chat_sessions, update_chat_session

load_dotenv()

VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")


def load_index_and_chunks():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        raise RuntimeError(
            "Vector store not found. Run create_db.py first to build the FAISS index."
        )
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


def load_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY/GOOGLE_API_KEY in environment.")
    genai.configure(api_key=api_key)
    # Prefer the most available first
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            _ = model.generate_content("ping")
            print(f"Using Gemini API model: {model_name}")
            return model
        except Exception:
            continue
    raise RuntimeError("Failed to initialize any Gemini API model.")


def search(index, query_vector, k=3):
    distances, indices = index.search(query_vector, k)
    return indices[0]


def init_vertex_for_embeddings():
    project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-ai-legal"
    location = os.getenv("GCP_LOCATION", "us-central1")
    vertexai.init(project=project_id, location=location)


def load_embedding_model():
    return TextEmbeddingModel.from_pretrained("text-embedding-004")


def embed_query(text):
    init_vertex_for_embeddings()
    model = load_embedding_model()
    values = model.get_embeddings([text])[0].values
    return np.array([values], dtype="float32")


def interactive_chat():
    # Load index and chunks
    index, chunks = load_index_and_chunks()

    # Load Gemini model
    model = load_gemini_model()

    # Conversation memory
    conversation_history = []
    
    # Chat session management
    current_chat_id = None
    current_chat_name = None
    is_first_query = True

    print("\nChatbot ready. Ask questions about your document.")
    print("Commands:")
    print("- Type 'summary' to generate a DETAILED agreement summary (600-700 words)")
    print("- Type 'exit' to quit")
    print()
    
    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        elif query.lower() == "summary":
            print("\nGenerating DETAILED agreement summary (600-700 words)...")
            try:
                # Load the first few chunks to get document content for summary
                if chunks:
                    # Combine first few chunks for summary generation
                    summary_text = " ".join(chunks[:5])  # Use first 5 chunks
                    analyzer = AgreementAnalyzer()
                    summary_result = analyzer.generate_detailed_summary(summary_text)
                    
                    print(f"\nAgreement Type: {summary_result['agreement_type']}")
                    print(f"Summary Length: {summary_result['word_count']} words")
                    print("\nDETAILED SUMMARY:")
                    print("=" * 60)
                    print(summary_result['summary'])
                    print("=" * 60)
                    
                    # Create chat session when detailed summary is generated
                    if is_first_query:
                        try:
                            # Get document name from chunks file path or use default
                            document_name = "Legal Agreement"
                            if os.path.exists(CHUNKS_PATH):
                                # Try to infer document name from the data directory
                                data_dir = os.path.dirname(CHUNKS_PATH)
                                summary_files = [f for f in os.listdir(data_dir) if f.endswith('_summary.txt')]
                                if summary_files:
                                    document_name = summary_files[0].replace('_summary.txt', '')
                            
                            # Generate chat name based on agreement type and summary
                            current_chat_name = generate_chat_name(
                                document_name=document_name,
                                document_summary=summary_result['summary']
                            )
                            current_chat_id = int(time.time() * 1000)
                            save_chat_session(
                                chat_id=current_chat_id,
                                chat_name=current_chat_name,
                                document_name=document_name
                            )
                            print(f"\n💬 Chat session created: '{current_chat_name}'")
                            is_first_query = False
                        except Exception as e:
                            print(f"Warning: Could not create chat session: {e}")
                    
                    # Add summary to conversation history
                    conversation_history.append(f"User: {query}")
                    conversation_history.append(f"Assistant: {summary_result['summary']}")
                    
                else:
                    print("No document content available for summary generation.")
            except Exception as e:
                print(f"Error generating detailed summary: {e}")
            continue

        # Note: Chat session is only created when detailed summary is generated
        # Regular queries don't create new chat sessions

        # Embed query and retrieve top-k chunks from FAISS
        try:
            q_vec = embed_query(query)
            top_idx = search(index, q_vec, k=3)
            context = [chunks[i] for i in top_idx]
        except Exception as e:
            print(f"Error embedding query: {e}")
            print("Falling back to using the first few chunks as context.")
            context = chunks[:3]

        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(conversation_history[-4:])  # Last 4 exchanges

        prompt = f"""You are a professional legal assistant who explains complex legal documents in simple, easy-to-understand language for people without legal backgrounds.

CONTEXT FROM DOCUMENT:
{"\n\n".join(context)}

{conversation_context}

USER QUESTION: {query}

INSTRUCTIONS:
- **Use simple language** - Explain legal terms in plain English that anyone can understand
- **Break down complexity** - Take complex legal concepts and make them clear and accessible
- **Provide practical understanding** - Help users grasp what the legal language actually means for them
- **Maintain professionalism** - Be helpful and informative while staying professional
- **Reference context** - Use previous conversation context when relevant
- **Give detailed answers when needed** - If the question requires steps, procedures, or comprehensive explanation, provide them

RESPONSE STYLE:
- Start with a clear, direct answer to the question
- **If the question requires detailed steps or procedures, provide them clearly**
- **Use bullet points and numbered lists when they make complex information easier to understand**
- Break down complex legal concepts into simple, understandable parts
- Use examples and practical explanations when helpful
- Avoid legal jargon and complex terminology
- Be informative and helpful without being overly casual
- **Adapt response length to the complexity of the question**

Remember: Your goal is to make legal documents understandable for non-legal professionals. Use clear, simple language while maintaining professional credibility. If a question needs detailed steps or comprehensive explanation, provide it."""

        try:
            resp = model.generate_content(prompt)
            response_text = getattr(resp, 'text', str(resp))
            print(f"\nAssistant:\n{response_text}\n")
            
            # Add to conversation history
            conversation_history.append(f"User: {query}")
            conversation_history.append(f"Assistant: {response_text}")
            
            # Update chat session with message count
            if current_chat_id:
                try:
                    update_chat_session(current_chat_id, {
                        "message_count": len(conversation_history) // 2,
                        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception as e:
                    print(f"Warning: Could not update chat session: {e}")
            
            # Keep only last 10 exchanges to manage memory
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")


if __name__ == "__main__":
    interactive_chat()


