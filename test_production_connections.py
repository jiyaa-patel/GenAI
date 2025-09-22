#!/usr/bin/env python3
"""
Test script to verify production service connections.
"""

import requests
import json
from datetime import datetime

# Production URLs
DJANGO_URL = "https://gen-ai-legal.uc.r.appspot.com"
FASTAPI_URL = "https://fastapi-dot-gen-ai-legal.uc.r.appspot.com"
FRONTEND_URL = "https://genai-silk-beta.vercel.app"

def test_service(name, url, endpoint=""):
    """Test if a service is responding."""
    try:
        full_url = f"{url}{endpoint}"
        print(f"Testing {name}: {full_url}")
        
        response = requests.get(full_url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ {name}: ONLINE (Status: {response.status_code})")
            return True
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: OFFLINE - {str(e)}")
        return False

def test_cors(service_name, url):
    """Test CORS configuration."""
    try:
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(url, headers=headers, timeout=30)
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"✅ {service_name}: CORS configured")
            return True
        else:
            print(f"⚠️  {service_name}: CORS may not be configured")
            return False
            
    except Exception as e:
        print(f"❌ {service_name}: CORS test failed - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("GenAI Legal - Production Connection Test")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\nTesting Service Availability...")
    print("-" * 40)
    
    # Test basic connectivity
    django_ok = test_service("Django Backend", DJANGO_URL, "/api/")
    fastapi_ok = test_service("FastAPI Service", FASTAPI_URL, "/api/health")
    frontend_ok = test_service("Frontend", FRONTEND_URL)
    
    print("\nTesting CORS Configuration...")
    print("-" * 40)
    
    # Test CORS
    if django_ok:
        test_cors("Django Backend", f"{DJANGO_URL}/api/")
    
    if fastapi_ok:
        test_cors("FastAPI Service", f"{FASTAPI_URL}/api/health")
    
    print("\nTesting API Endpoints...")
    print("-" * 40)
    
    # Test specific endpoints
    if fastapi_ok:
        try:
            response = requests.get(f"{FASTAPI_URL}/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FastAPI Root: {data.get('message', 'OK')}")
            else:
                print(f"⚠️  FastAPI Root: Status {response.status_code}")
        except Exception as e:
            print(f"❌ FastAPI Root: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Production URLs:")
    print(f"Django Backend:  {DJANGO_URL}")
    print(f"FastAPI Service: {FASTAPI_URL}")
    print(f"Frontend:        {FRONTEND_URL}")
    print("=" * 60)
    
    # Summary
    services_ok = sum([django_ok, fastapi_ok, frontend_ok])
    print(f"\nSummary: {services_ok}/3 services are online")
    
    if services_ok == 3:
        print("🎉 All services are connected and working!")
    elif services_ok >= 2:
        print("⚠️  Most services are working, check the failed ones")
    else:
        print("❌ Multiple services are down, check deployments")

if __name__ == "__main__":
    main()