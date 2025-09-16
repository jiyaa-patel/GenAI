#!/usr/bin/env python3
"""
FastAPI Runner Script
Starts the Legal Agreement Analyzer API with proper configuration.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Ensure Google credentials and Vertex defaults are set for Vertex AI SDK
try:
    project_root = current_dir.parent  # backEnd directory
    credentials_path = project_root / "credentials" / "gen-ai-legal-536c695ad0a1.json"

    # Set GOOGLE_APPLICATION_CREDENTIALS if not set
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and credentials_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
        print(f"✓ GOOGLE_APPLICATION_CREDENTIALS set to {credentials_path}")

    # Set sensible defaults for Vertex AI if not provided
    os.environ.setdefault("GCP_PROJECT", os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-ai-legal"))
    os.environ.setdefault("GCP_LOCATION", os.environ.get("VERTEX_LOCATION", "us-central1"))
except Exception as e:
    print(f"⚠ Warning: Could not set Google credentials defaults: {e}")

# Load user contexts on startup
try:
    from auth import load_contexts_from_file
    load_contexts_from_file()
    print("✓ Loaded user contexts from file")
except Exception as e:
    print(f"⚠ Warning: Could not load user contexts: {e}")

if __name__ == "__main__":
    print("🚀 Starting Legal Agreement Analyzer API...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔐 Authentication: JWT Bearer Token required")
    print("👤 User Context: Per-user conversation management enabled")
    print("-" * 50)
    
    # Run the FastAPI application
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,  # Changed from 8000 to avoid conflict with Django
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
