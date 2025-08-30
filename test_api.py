#!/usr/bin/env python3
"""
Test script for MindT2I Flask API
Author: lycosa9527
Made by MindSpring Team
"""

import requests
import json
import time
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:9528"
TEST_PROMPTS = [
    "传统中式庭院，优雅的书法卷轴，古典家具和青花瓷花瓶",
    "宁静的日式花园，盛开的樱花，传统木制建筑，宁静氛围",
    "未来城市景观，飞行汽车，霓虹灯，日落时分的摩天大楼",
    "一只猫",  # 简单提示词测试增强
    "美丽的日落",  # 简单提示词测试增强 (3+ characters)
    "数学课"  # 教育背景提示词
]

def test_health_check():
    """Test the health check endpoint"""
    logger.info("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check passed - Status: {data['status']}")
            logger.info(f"API Key configured: {data.get('system', {}).get('api_key_configured', 'Unknown')}")
            logger.info(f"Free space: {data.get('system', {}).get('free_space_mb', 'Unknown')} MB")
            logger.info(f"Stored images: {data.get('system', {}).get('stored_images', 'Unknown')}")
            return True
        else:
            logger.error(f"Health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check error - Details: {e}")
        return False

def test_image_generation(prompt, size="1664*928"):
    """Test image generation with a given prompt"""
    logger.info("Testing image generation...")
    logger.info(f"Prompt: {prompt[:100]}...")
    logger.info(f"Size: {size}")
    
    payload = {
        "prompt": prompt,
        "size": size,
        "negative_prompt": "",
        "watermark": False,  # Set to False for clean educational materials
        "prompt_extend": False  # Set to False since we use Qwen Turbo via DashScope for enhancement
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/generate-image",
            json=payload,
            timeout=180  # 3 minutes timeout
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("Image generated successfully")
                logger.info(f"Image URL: {data['image_url']}")
                logger.info(f"Filename: {data['filename']}")
                logger.info(f"Generation time: {end_time - start_time:.2f} seconds")
                
                # Log prompt enhancement information
                if data.get('prompt_enhanced'):
                    logger.info(f"Prompt enhanced: {data.get('original_prompt', 'N/A')} -> {data.get('enhanced_prompt', 'N/A')[:100]}...")
                else:
                    logger.info("No prompt enhancement applied")
                
                # Test image retrieval
                test_image_retrieval(data['image_url'])
                return True
            else:
                logger.error(f"Image generation failed - Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            logger.error(f"HTTP error - Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout - image generation is taking longer than expected")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error - Details: {e}")
        return False

def test_image_retrieval(image_url):
    """Test retrieving the generated image"""
    logger.info("Testing image retrieval...")
    try:
        # image_url is now a full URL, so we can use it directly
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            content_length = len(response.content)
            logger.info(f"Image retrieved successfully - Size: {content_length} bytes")
            return True
        else:
            logger.error(f"Image retrieval failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Image retrieval error - Details: {e}")
        return False

def test_invalid_requests():
    """Test various invalid request scenarios"""
    logger.info("Testing invalid requests...")
    
    # Test missing prompt
    logger.info("Testing missing prompt...")
    try:
        response = requests.post(f"{BASE_URL}/generate-image", json={}, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            logger.info("Correctly rejected missing prompt")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.error(f"Unexpected response - Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing missing prompt - Details: {e}")
    
    # Test empty prompt
    logger.info("Testing empty prompt...")
    try:
        response = requests.post(f"{BASE_URL}/generate-image", json={"prompt": ""}, timeout=10)
        if response.status_code == 400:
            error_data = response.json()
            logger.info("Correctly rejected empty prompt")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.error(f"Unexpected response - Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing empty prompt - Details: {e}")
    
    # Test invalid JSON
    logger.info("Testing invalid JSON...")
    try:
        response = requests.post(
            f"{BASE_URL}/generate-image",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 400:
            error_data = response.json()
            logger.info("Correctly rejected invalid JSON")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.error(f"Unexpected response - Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing invalid JSON - Details: {e}")

def test_security_features():
    """Test security features and protections"""
    logger.info("Testing security features...")
    
    # Test rate limiting
    logger.info("Testing rate limiting...")
    try:
        responses = []
        for i in range(12):  # Try to exceed 10 per minute limit
            response = requests.post(f"{BASE_URL}/generate-image", 
                                  json={"prompt": f"test rate limit {i}"}, 
                                  timeout=10)
            responses.append(response.status_code)
            if response.status_code == 429:  # Rate limited
                break
        
        logger.info(f"Made {len(responses)} requests")
        if 429 in responses:
            logger.info("✅ Rate limiting working correctly")
        else:
            logger.warning("⚠️ Rate limiting not detected")
    except Exception as e:
        logger.error(f"Error testing rate limiting - Details: {e}")
    
    # Test path traversal protection
    logger.info("Testing path traversal protection...")
    try:
        response = requests.get(f"{BASE_URL}/temp_images/../../../etc/passwd", timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            logger.info("✅ Path traversal protection working (Flask routing protection)")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.warning("⚠️ Path traversal protection may be weak")
    except Exception as e:
        logger.error(f"Error testing path traversal - Details: {e}")
    
    # Test XSS filename protection
    logger.info("Testing XSS filename protection...")
    try:
        response = requests.get(f"{BASE_URL}/temp_images/<script>alert('xss')</script>.jpg", timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            logger.info("✅ XSS filename protection working (Flask routing protection)")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.warning("⚠️ XSS filename protection may be weak")
    except Exception as e:
        logger.error(f"Error testing XSS protection - Details: {e}")

def test_new_endpoints():
    """Test new endpoints added in the improved version"""
    logger.info("Testing new endpoints...")
    
    # Test configuration endpoint
    logger.info("Testing configuration endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=10)
        if response.status_code == 200:
            config_data = response.json()
            logger.info("✅ Configuration endpoint working")
            logger.info(f"Default image size: {config_data.get('config', {}).get('default_image_size', 'Unknown')}")
            logger.info(f"Prompt enhancement: {config_data.get('config', {}).get('prompt_enhancement_enabled', 'Unknown')}")
        else:
            logger.error(f"Configuration endpoint error: {response.text}")
    except Exception as e:
        logger.error(f"Error testing configuration endpoint - Details: {e}")
    
    # Test error handling
    logger.info("Testing error handling...")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent", timeout=10)
        if response.status_code == 404:
            error_data = response.json()
            logger.info("✅ 404 error handling working")
            logger.info(f"Error code: {error_data.get('error_code', 'None')}")
        else:
            logger.warning("⚠️ Unexpected response for 404")
    except Exception as e:
        logger.error(f"Error testing 404 handling - Details: {e}")

def main():
    """Main test function"""
    logger.info("MindT2I API Test Suite")
    logger.info("=" * 50)
    logger.info("Made by MindSpring Team | Author: lycosa9527")
    logger.info("")
    
    # Check if server is running
    if not test_health_check():
        logger.error("Server is not running or not accessible!")
        logger.error("Please start the Flask application first:")
        logger.error("python app.py")
        return
    
    # Test image generation with different prompts
    success_count = 0
    total_tests = len(TEST_PROMPTS)
    
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        logger.info(f"Test {i}/{total_tests}")
        if test_image_generation(prompt):
            success_count += 1
    
    # Test invalid requests
    test_invalid_requests()
    
    # Test security features
    test_security_features()
    
    # Test new endpoints
    test_new_endpoints()
    
    # Summary
    logger.info("Test Summary")
    logger.info("=" * 50)
    logger.info(f"Successful tests: {success_count}/{total_tests}")
    logger.info(f"Failed tests: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        logger.info("All tests passed! The API is working correctly.")
    else:
        logger.warning(f"{total_tests - success_count} test(s) failed. Check the logs above for details.")
    
    logger.info(f"API Documentation: {BASE_URL}/")
    logger.info(f"Health Check: {BASE_URL}/health")
    logger.info(f"Configuration: {BASE_URL}/config")

if __name__ == "__main__":
    main()
