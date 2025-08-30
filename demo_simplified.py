#!/usr/bin/env python3
"""
Demo script for MindT2I simplified API usage
Shows how easy it is to use the API with just a prompt
"""

import requests
import json

def demo_minimal_requests():
    """Demonstrate minimal API requests with just a prompt"""
    print("🚀 MindT2I Simplified API Demo")
    print("=" * 50)
    
    # Test minimal request to JSON endpoint
    print("\n1️⃣ Testing minimal request to JSON endpoint...")
    url = "http://localhost:9528/generate-image"
    minimal_payload = {"prompt": "A friendly cat in a bright classroom"}
    
    try:
        response = requests.post(url, json=minimal_payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Image generated with minimal request")
            print(f"   Image URL: {result['image_url']}")
            print(f"   Markdown: {result['markdown_image']}")
            print(f"   Prompt enhanced: {result['prompt_enhanced']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test minimal request to plain text endpoint
    print("\n2️⃣ Testing minimal request to plain text endpoint...")
    url_text = "http://localhost:9528/generate-image-text"
    minimal_payload_text = {"prompt": "A colorful butterfly in a garden"}
    
    try:
        response = requests.post(url_text, json=minimal_payload_text, timeout=120)
        if response.status_code == 200:
            plain_text = response.text
            print(f"✅ Success! Plain text output with minimal request")
            print(f"   Output: {plain_text}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test with all parameters for comparison
    print("\n3️⃣ Testing with all parameters for comparison...")
    full_payload = {
        "prompt": "A majestic mountain landscape",
        "size": "1328*1328",
        "watermark": False,
        "negative_prompt": "dark, gloomy",
        "prompt_extend": True
    }
    
    try:
        response = requests.post(url, json=full_payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Full parameter request also works")
            print(f"   Image URL: {result['image_url']}")
            print(f"   Size: {result['size']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def show_api_comparison():
    """Show the difference between old and new API usage"""
    print("\n" + "=" * 50)
    print("📊 API Usage Comparison")
    print("=" * 50)
    
    print("\n🔴 Old Way (Required all parameters):")
    print("""{
    "prompt": "a cat",
    "size": "1664*928",
    "watermark": false,
    "negative_prompt": "",
    "prompt_extend": false
}""")
    
    print("\n🟢 New Way (Minimal - Recommended):")
    print("""{
    "prompt": "a cat"
}""")
    
    print("\n🟡 New Way (With some parameters):")
    print("""{
    "prompt": "a cat",
    "size": "1328*1328"
}""")
    
    print("\n💡 Benefits of the new simplified approach:")
    print("   • Only prompt is required")
    print("   • All other parameters have sensible defaults")
    print("   • Faster development and testing")
    print("   • Cleaner, more readable code")
    print("   • Backward compatible with full parameter usage")

if __name__ == "__main__":
    try:
        demo_minimal_requests()
        show_api_comparison()
        print("\n🎉 Demo completed successfully!")
        print("   The API now supports minimal requests with just a prompt!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("   Make sure the Flask application is running on localhost:9528")
