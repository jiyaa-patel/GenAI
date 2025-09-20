#!/usr/bin/env python
import os
from google.cloud import storage

# Test GCS connection
try:
    print("Testing GCS connection...")
    
    # Check credentials
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"Credentials path: {creds_path}")
    
    if creds_path and os.path.exists(creds_path):
        print("Credentials file exists")
    else:
        print("Credentials file not found")
        # Try to set it from the project structure
        project_creds = "credentials/gen-ai-legal-536c695ad0a1.json"
        if os.path.exists(project_creds):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(project_creds)
            print(f"Set credentials to: {os.path.abspath(project_creds)}")
        else:
            print("No credentials found in project either")
    
    # Test storage client
    client = storage.Client()
    print("Storage client created")
    
    # Test bucket access
    bucket_name = "legal-agreement-analyzer-gen-ai-legal"
    bucket = client.bucket(bucket_name)
    
    # Try to list some blobs (this will fail if bucket doesn't exist or no access)
    blobs = list(client.list_blobs(bucket, max_results=1))
    print(f"Bucket '{bucket_name}' accessible")
    
    # Test upload
    test_blob = bucket.blob("test/connection_test.txt")
    test_blob.upload_from_string("Connection test successful")
    print("Upload test successful")
    
    # Clean up
    test_blob.delete()
    print("Delete test successful")
    
    print("\nGCS is properly configured!")
    
except Exception as e:
    print(f"GCS Error: {e}")
    import traceback
    traceback.print_exc()