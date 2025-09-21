#!/usr/bin/env python
import os
from google.cloud import storage

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath("credentials/gen-ai-legal-6480fd4d86ab.json")

try:
    client = storage.Client()
    
    # Try different bucket names (must be globally unique)
    project_id = "gen-ai-legal"  # Your project ID
    bucket_names = [
        f"legal-agreement-analyzer-{project_id}",
        f"genai-legal-docs-{project_id}",
        f"pactai-documents-{project_id}"
    ]
    
    for bucket_name in bucket_names:
        try:
            print(f"Trying to create bucket: {bucket_name}")
            bucket = client.create_bucket(bucket_name, location="US")
            print(f"Created bucket: {bucket_name}")
            
            # Test upload
            test_blob = bucket.blob("test/setup_test.txt")
            test_blob.upload_from_string("Bucket setup successful")
            print("Upload test successful")
            
            # Update environment variable
            print(f"\nUpdate your .env file:")
            print(f"GCS_BUCKET_NAME={bucket_name}")
            
            break
            
        except Exception as e:
            if "already exists" in str(e) or "already owned" in str(e):
                print(f"Bucket {bucket_name} already exists, trying to use it...")
                try:
                    bucket = client.bucket(bucket_name)
                    test_blob = bucket.blob("test/setup_test.txt")
                    test_blob.upload_from_string("Bucket test successful")
                    print(f"Using existing bucket: {bucket_name}")
                    print(f"\nUpdate your .env file:")
                    print(f"GCS_BUCKET_NAME={bucket_name}")
                    break
                except Exception as e2:
                    print(f"Cannot access bucket {bucket_name}: {e2}")
            else:
                print(f"Failed to create {bucket_name}: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()