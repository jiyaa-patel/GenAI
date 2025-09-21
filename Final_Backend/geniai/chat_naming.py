import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def load_gemini_model():
    """Load Gemini API model for chat name generation."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY/GOOGLE_API_KEY in environment.")
    genai.configure(api_key=api_key)
    
    # Prefer the most available model for quick responses
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            _ = model.generate_content("ping")
            print(f"Using Gemini API model for chat naming: {model_name}")
            return model
        except Exception:
            continue
    raise RuntimeError("Failed to initialize any Gemini API model for chat naming.")

def generate_chat_name(document_name, document_summary=None, first_query=None):
    """
    Generate a meaningful chat name based on document content and context.
    
    Args:
        document_name (str): Name of the uploaded document
        document_summary (str, optional): Summary of the document content
        first_query (str, optional): First user query in the chat
    
    Returns:
        str: Generated chat name
    """
    try:
        model = load_gemini_model()
        
        # Create context for name generation
        context_parts = []
        
        if document_name:
            context_parts.append(f"Document: {document_name}")
        
        if document_summary:
            # Use first 200 characters of summary for context
            summary_preview = document_summary[:200] + "..." if len(document_summary) > 200 else document_summary
            context_parts.append(f"Content: {summary_preview}")
        
        if first_query:
            context_parts.append(f"First question: {first_query}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Generate a concise, descriptive chat name (maximum 50 characters) for a legal agreement analysis session.

Context:
{context}

Requirements:
- Be specific and descriptive about the legal agreement type
- Include the agreement type or main legal topic
- Keep it under 50 characters
- Use title case
- Make it professional and legal-focused
- Avoid generic names like "Document Chat" or "PDF Discussion"

Examples of good names for legal agreements:
- "Employment Contract Review"
- "Lease Agreement Analysis" 
- "Service Agreement Chat"
- "Purchase Contract Q&A"
- "Partnership Agreement Review"
- "Loan Agreement Discussion"
- "NDA Terms Analysis"

Generate only the chat name, nothing else:"""

        response = model.generate_content(prompt)
        chat_name = getattr(response, 'text', str(response)).strip()
        
        # Clean up the response and ensure it meets requirements
        chat_name = chat_name.replace('"', '').replace("'", "").strip()
        
        # Fallback if name is too long or empty
        if len(chat_name) > 50 or not chat_name:
            # Generate a fallback name based on document name
            doc_name_clean = os.path.splitext(document_name)[0] if document_name else "Document"
            chat_name = f"{doc_name_clean[:30]} Chat"
        
        return chat_name
        
    except Exception as e:
        print(f"Error generating chat name: {e}")
        # Fallback to document-based name
        if document_name:
            doc_name_clean = os.path.splitext(document_name)[0]
            return f"{doc_name_clean[:30]} Chat"
        else:
            return f"Document Chat {datetime.now().strftime('%m/%d')}"

def generate_chat_name_from_query(document_name, query):
    """
    Generate a chat name based on the first user query.
    This is used when a user starts asking questions without uploading a document.
    """
    try:
        model = load_gemini_model()
        
        prompt = f"""Generate a concise, descriptive chat name (maximum 50 characters) for a legal agreement chat session.

Document: {document_name or 'Legal Agreement'}
First Query: {query}

Requirements:
- Be specific and descriptive about the legal agreement topic
- Include the main legal subject or agreement type
- Keep it under 50 characters
- Use title case
- Make it professional and legal-focused

Examples for legal agreements:
- "Employment Contract Review"
- "Lease Terms Analysis"
- "Service Agreement Chat"
- "Contract Questions Session"
- "Legal Document Review"
- "Agreement Terms Discussion"

Generate only the chat name, nothing else:"""

        response = model.generate_content(prompt)
        chat_name = getattr(response, 'text', str(response)).strip()
        
        # Clean up the response
        chat_name = chat_name.replace('"', '').replace("'", "").strip()
        
        # Fallback if name is too long or empty
        if len(chat_name) > 50 or not chat_name:
            # Extract key words from query for fallback
            words = query.split()[:3]  # First 3 words
            chat_name = f"{' '.join(words)} Chat"
            if len(chat_name) > 50:
                chat_name = f"{words[0]} Chat"
        
        return chat_name
        
    except Exception as e:
        print(f"Error generating chat name from query: {e}")
        # Fallback
        if document_name:
            doc_name_clean = os.path.splitext(document_name)[0]
            return f"{doc_name_clean[:30]} Chat"
        else:
            return f"Chat {datetime.now().strftime('%m/%d %H:%M')}"

def save_chat_session(chat_id, chat_name, document_name, document_path=None, created_at=None):
    """
    Save chat session metadata to a JSON file.
    """
    if created_at is None:
        created_at = datetime.now().isoformat()
    
    chat_data = {
        "id": chat_id,
        "name": chat_name,
        "document_name": document_name,
        "document_path": document_path,
        "created_at": created_at,
        "last_updated": created_at,
        "message_count": 0
    }
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to chat sessions file
    sessions_file = os.path.join(data_dir, "chat_sessions.json")
    
    # Load existing sessions
    sessions = []
    if os.path.exists(sessions_file):
        try:
            with open(sessions_file, "r", encoding="utf-8") as f:
                sessions = json.load(f)
        except Exception as e:
            print(f"Error loading chat sessions: {e}")
            sessions = []
    
    # Add new session
    sessions.append(chat_data)
    
    # Save updated sessions
    try:
        with open(sessions_file, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        print(f"Chat session saved: {chat_name}")
    except Exception as e:
        print(f"Error saving chat session: {e}")

def load_chat_sessions():
    """
    Load all chat sessions from the JSON file.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    sessions_file = os.path.join(data_dir, "chat_sessions.json")
    
    if not os.path.exists(sessions_file):
        return []
    
    try:
        with open(sessions_file, "r", encoding="utf-8") as f:
            sessions = json.load(f)
        return sessions
    except Exception as e:
        print(f"Error loading chat sessions: {e}")
        return []

def update_chat_session(chat_id, updates):
    """
    Update an existing chat session.
    """
    sessions = load_chat_sessions()
    
    for session in sessions:
        if session["id"] == chat_id:
            session.update(updates)
            session["last_updated"] = datetime.now().isoformat()
            break
    
    # Save updated sessions
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    sessions_file = os.path.join(data_dir, "chat_sessions.json")
    
    try:
        with open(sessions_file, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error updating chat session: {e}")
        return False

if __name__ == "__main__":
    # Test the chat naming functionality
    print("Testing chat name generation...")
    
    # Test with document name and summary
    test_name = generate_chat_name(
        "employment_contract.pdf",
        "This employment agreement outlines the terms and conditions for a software engineer position, including salary, benefits, and termination clauses.",
        "What are the key terms of this employment contract?"
    )
    print(f"Generated name: {test_name}")
    
    # Test with just query
    test_name2 = generate_chat_name_from_query(
        "lease_agreement.pdf",
        "What are the rental terms and conditions?"
    )
    print(f"Generated name from query: {test_name2}")
