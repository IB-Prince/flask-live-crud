#!/usr/bin/env python3
"""
Simple startup script to test if the app can start
"""
import os
import sys

def main():
    try:
        print("🚀 Testing Flask app startup...")
        
        # Import the app
        from app import app
        
        print("✅ App imported successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            print(f"✅ Health check response: {response.status_code}")
            print(f"✅ Health check data: {response.get_json()}")
        
        print("✅ App is ready to start!")
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
