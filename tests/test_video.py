#!/usr/bin/env python3
"""
Test video generation endpoint
"""

import requests

def test_video_endpoint():
    """Test the /generate-video endpoint"""
    
    print("\n" + "=" * 70)
    print("Testing Video Generation Endpoint")
    print("=" * 70)
    
    url = "http://localhost:9528/generate-video"
    
    test_cases = [
        {
            "name": "Simple video request",
            "prompt": "Generate a video of cats playing in the garden"
        },
        {
            "name": "Chinese video request",
            "prompt": "生成一个视频：小猫在月光下奔跑"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test['name']} ---")
        print(f"Prompt: {test['prompt']}")
        
        try:
            response = requests.post(
                url,
                json={"prompt": test['prompt']},
                timeout=300  # 5 minutes for video generation
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # Plain text response
                plain_text = response.text
                print(f"\nResponse (Plain Text):")
                print(plain_text)
                print("\n✅ Video generation successful!")
            else:
                print(f"\n❌ Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("\n⏱️  Request timed out (video generation can take 1-5 minutes)")
        except Exception as e:
            print(f"\n❌ Exception: {e}")
    
    print("\n" + "=" * 70)
    print("Note: Video generation takes 1-5 minutes. Be patient!")
    print("Output format: [video-download link][URL]")
    print("=" * 70)


def test_intelligent_endpoint():
    """Test the /generate endpoint with video keyword"""
    
    print("\n" + "=" * 70)
    print("Testing Intelligent Generation Endpoint (with video keyword)")
    print("=" * 70)
    
    url = "http://localhost:9528/generate"
    
    prompt = "Generate a video of birds flying in the sky"
    
    print(f"\nPrompt: {prompt}")
    print("Expected: Should detect 'video' keyword and route to video generation")
    
    try:
        response = requests.post(
            url,
            json={"prompt": prompt},
            timeout=300
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nDetected type: {result.get('type')}")
            print(f"URL: {result.get('url', 'N/A')[:80]}...")
            
            if 'text' in result:
                print(f"\nPlain text output:")
                print(result['text'])
            
            if 'intent_analysis' in result:
                analysis = result['intent_analysis']
                print(f"\nIntent Analysis:")
                print(f"  Confidence: {analysis.get('confidence')}")
                print(f"  Reasoning: {analysis.get('reasoning')}")
            
            print("\n✅ Intelligent routing successful!")
        else:
            print(f"\n❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out")
    except Exception as e:
        print(f"\n❌ Exception: {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🎬 MindT2I Video Generation Tests")
    print("Make sure the server is running: python main.py")
    
    # Test dedicated video endpoint
    test_video_endpoint()
    
    # Test intelligent routing
    test_intelligent_endpoint()

