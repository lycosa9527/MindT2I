#!/usr/bin/env python3
"""
Test script for MindT2I plain text output functionality
Demonstrates both the dedicated plain text endpoint and the plain_text parameter
"""

import requests
import json

def test_plain_text_endpoint():
    """Test the dedicated plain text endpoint"""
    print("🧪 Testing dedicated plain text endpoint...")
    
    url = "http://localhost:9528/generate-image-text"
    payload = {
        "prompt": "A friendly cat in a bright science classroom",
        "size": "1328*1328",
        "watermark": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            plain_text = response.text
            print(f"✅ Success! Plain text output:")
            print(f"   {plain_text}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"   Response length: {len(plain_text)} characters")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_plain_text_parameter():
    """Test the plain_text parameter in the regular endpoint"""
    print("\n🧪 Testing plain_text parameter in regular endpoint...")
    
    url = "http://localhost:9528/generate-image"
    payload = {
        "prompt": "A beautiful sunset over mountains",
        "size": "1664*928",
        "watermark": False,
        "plain_text": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            plain_text = response.text
            print(f"✅ Success! Plain text output:")
            print(f"   {plain_text}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"   Response length: {len(plain_text)} characters")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_json_endpoint():
    """Test the regular JSON endpoint for comparison"""
    print("\n🧪 Testing regular JSON endpoint for comparison...")
    
    url = "http://localhost:9528/generate-image"
    payload = {
        "prompt": "A serene Japanese garden",
        "size": "1140*1472",
        "watermark": False,
        "plain_text": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! JSON response:")
            print(f"   Image URL: {result.get('image_url', 'Not found')}")
            print(f"   Markdown: {result.get('markdown_image', 'Not found')}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"   Response length: {len(response.text)} characters")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 MindT2I Plain Text Output Test")
    print("=" * 50)
    
    # Test all three scenarios
    test_plain_text_endpoint()
    test_plain_text_parameter()
    test_json_endpoint()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    print("\n📝 Summary:")
    print("   • /generate-image-text: Returns pure plain text")
    print("   • /generate-image?plain_text=true: Returns plain text when requested")
    print("   • /generate-image: Returns JSON with markdown_image field")
    print("\n💡 Use the plain text endpoints when you need just the markdown syntax")
    print("   without any JSON formatting or additional metadata.")
