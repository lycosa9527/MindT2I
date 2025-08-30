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
    "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书义本生知人机同道善思新，右书通云赋智乾坤启数高志远， 横批智启通义，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
    "A serene Japanese garden with cherry blossoms in full bloom, traditional wooden architecture, peaceful atmosphere",
    "A futuristic cityscape with flying cars, neon lights, and towering skyscrapers at sunset",
    "a cat",  # Simple prompt to test enhancement
    "sunset",  # Very simple prompt to test enhancement
    "math class"  # Educational context prompt
]

def test_health_check():
    """Test the health check endpoint"""
    logger.info("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check passed - Status: {data['status']}")
            logger.info(f"API Key configured: {data['api_key_configured']}")
            logger.info(f"Timestamp: {data['timestamp']}")
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
        "watermark": True,
        "prompt_extend": False  # Set to False since we use Qwen Turbo for enhancement
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
        response = requests.get(f"{BASE_URL}{image_url}", timeout=30)
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
            logger.info("Correctly rejected missing prompt")
        else:
            logger.error(f"Unexpected response - Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing missing prompt - Details: {e}")
    
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
            logger.info("Correctly rejected invalid JSON")
        else:
            logger.error(f"Unexpected response - Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing invalid JSON - Details: {e}")

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

if __name__ == "__main__":
    main()
