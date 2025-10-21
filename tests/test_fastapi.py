#!/usr/bin/env python3
"""
Test script for MindT2I v2.0 FastAPI Edition
============================================

Tests the new FastAPI-based image generation API.
"""

import asyncio
import aiohttp
import time


async def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("🏥 Testing Health Endpoint")
    print("=" * 60)
    
    url = "http://localhost:9528/health"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health Check: {data['status']}")
                print(f"   Service: {data['service']}")
                print(f"   Version: {data['version']}")
            else:
                print(f"❌ Health check failed: {response.status}")


async def test_status():
    """Test status endpoint"""
    print("\n" + "=" * 60)
    print("📊 Testing Status Endpoint")
    print("=" * 60)
    
    url = "http://localhost:9528/status"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Status: {data['status']}")
                print(f"   Framework: {data['framework']}")
                print(f"   Uptime: {data['uptime_seconds']}s")
                print(f"   Memory: {data['memory_percent']}%")
            else:
                print(f"❌ Status check failed: {response.status}")


async def test_image_generation():
    """Test image generation endpoint"""
    print("\n" + "=" * 60)
    print("🎨 Testing Image Generation Endpoint (JSON)")
    print("=" * 60)
    
    url = "http://localhost:9528/generate-image"
    payload = {
        "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置",
        "size": "1328*1328",
        "watermark": False,
        "prompt_extend": True
    }
    
    print(f"Prompt: {payload['prompt'][:50]}...")
    print("Generating image (this may take 30-60 seconds)...")
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                elapsed = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Image Generated Successfully!")
                    print(f"   Time: {elapsed:.1f}s")
                    print(f"   Image URL: {data['image_url']}")
                    print(f"   Filename: {data['filename']}")
                    print(f"   Size: {data['size']}")
                    print(f"   Prompt Enhanced: {data['prompt_enhanced']}")
                    if data['prompt_enhanced']:
                        print(f"   Enhanced Prompt: {data['enhanced_prompt'][:100]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ Generation failed: {response.status}")
                    print(f"   Error: {error_text}")
    except asyncio.TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_image_generation_text():
    """Test plain text image generation endpoint"""
    print("\n" + "=" * 60)
    print("📝 Testing Image Generation Endpoint (Plain Text)")
    print("=" * 60)
    
    url = "http://localhost:9528/generate-image-text"
    payload = {
        "prompt": "一只可爱的小猫在阳光明媚的花园里玩耍",
        "size": "1328*1328"
    }
    
    print(f"Prompt: {payload['prompt']}")
    print("Generating image (this may take 30-60 seconds)...")
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                elapsed = time.time() - start_time
                
                if response.status == 200:
                    text = await response.text()
                    print(f"✅ Image Generated Successfully!")
                    print(f"   Time: {elapsed:.1f}s")
                    print(f"   Plain Text Output: {text}")
                else:
                    error_text = await response.text()
                    print(f"❌ Generation failed: {response.status}")
                    print(f"   Error: {error_text}")
    except asyncio.TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_minimal_request():
    """Test minimal request with only prompt"""
    print("\n" + "=" * 60)
    print("⚡ Testing Minimal Request (Only Prompt)")
    print("=" * 60)
    
    url = "http://localhost:9528/generate-image"
    payload = {
        "prompt": "A beautiful sunset over mountains"
    }
    
    print(f"Prompt: {payload['prompt']}")
    print("Generating image with default settings...")
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                elapsed = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Minimal Request Works!")
                    print(f"   Time: {elapsed:.1f}s")
                    print(f"   Image URL: {data['image_url']}")
                    print(f"   Default Size Used: {data['size']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Generation failed: {response.status}")
                    print(f"   Error: {error_text}")
    except asyncio.TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 MindT2I v2.0 FastAPI Edition - Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  python main.py")
    print("\nor")
    print("  uvicorn main:app --reload")
    
    try:
        # Quick tests
        await test_health()
        await test_status()
        
        # Image generation tests (slower)
        print("\n" + "=" * 60)
        print("⚠️  The following tests will take 1-2 minutes each")
        print("=" * 60)
        
        await test_minimal_request()
        await test_image_generation()
        await test_image_generation_text()
        
        print("\n" + "=" * 60)
        print("🎉 All Tests Completed!")
        print("=" * 60)
        print("\n💡 Check the generated images in the temp_images/ folder")
        print("💡 View API docs at: http://localhost:9528/docs")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

