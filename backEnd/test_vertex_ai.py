#!/usr/bin/env python3
"""
Simple test script to verify Vertex AI connectivity and configuration.
Run this script to test if your Vertex AI setup is working correctly.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from ai.config import VERTEX_AI_CONFIG
import vertexai
from vertexai.generative_models import GenerativeModel

def test_vertex_ai_connection():
    """Test Vertex AI connection and basic functionality."""
    try:
        print("Testing Vertex AI connection...")
        print(f"Project ID: {VERTEX_AI_CONFIG['project_id']}")
        print(f"Location: {VERTEX_AI_CONFIG['location']}")
        print(f"Model: {VERTEX_AI_CONFIG['model_name']}")
        print("-" * 50)
        
        # Initialize Vertex AI
        vertexai.init(
            project=VERTEX_AI_CONFIG['project_id'],
            location=VERTEX_AI_CONFIG['location']
        )
        
        # Create model instance
        model = GenerativeModel(VERTEX_AI_CONFIG['model_name'])
        
        # Test with document content directly
        test_content = "This is a test document about artificial intelligence and machine learning. It discusses various applications and benefits of AI technology."
        response = model.generate_content(test_content)
        
        print("✅ Vertex AI connection successful!")
        print(f"Response: {response.text}")
        print("\n🎉 Your Vertex AI setup is working correctly!")
        
        return True
        
    except Exception as e:
        print("❌ Vertex AI connection failed!")
        print(f"Error: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you have set up Google Cloud authentication")
        print("2. Verify your project ID is correct")
        print("3. Ensure Vertex AI API is enabled in your Google Cloud Console")
        print("4. Check that you have the necessary permissions")
        return False

if __name__ == "__main__":
    print("🧪 Vertex AI Configuration Test")
    print("=" * 50)
    
    # Test Vertex AI connection
    success = test_vertex_ai_connection()
    
    if success:
        print("\n✅ All tests passed! You're ready to use the document processing feature.")
    else:
        print("\n❌ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)
