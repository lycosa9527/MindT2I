"""
Multimodal LLM Client for MindT2I
==================================

This module provides async interfaces for DashScope multimodal APIs:
- Qwen Image Plus for text-to-image generation
- Qwen Turbo for prompt enhancement
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional
from config.settings import config

logger = logging.getLogger(__name__)


class MultiModalClient:
    """Async client for DashScope MultiModal Conversation API (Qwen Image Plus)"""
    
    def __init__(self):
        """Initialize MultiModal client"""
        self.api_key = config.DASHSCOPE_API_KEY
        self.base_url = config.DASHSCOPE_BASE_URL
        self.model = config.QWEN_IMAGE_MODEL
        self.timeout = config.API_TIMEOUT
        
        # Construct the full API URL
        self.api_url = f"{self.base_url}/services/aigc/multimodal-generation/generation"
        
        logger.info(f"MultiModalClient initialized with model: {self.model}")
    
    async def generate_image(
        self, 
        prompt: str,
        size: str = "1328*1328",
        watermark: bool = False,
        negative_prompt: str = "",
        prompt_extend: bool = True
    ) -> Dict:
        """
        Generate image using Qwen Image Plus via DashScope MultiModal API
        
        Args:
            prompt: Text description for image generation
            size: Image size (e.g., "1328*1328")
            watermark: Whether to add watermark
            negative_prompt: Negative prompt for generation
            prompt_extend: Whether to extend the prompt
            
        Returns:
            Dict containing the API response
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Prepare messages in MultiModal format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "size": size,
                    "watermark": watermark,
                    "prompt_extend": prompt_extend,
                    "negative_prompt": negative_prompt
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Sending request to DashScope MultiModal API - Size: {size}, Watermark: {watermark}")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"MultiModal API response received successfully")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"MultiModal API error {response.status}: {error_text}")
                        raise Exception(f"MultiModal API error: {response.status} - {error_text}")
                        
        except asyncio.TimeoutError:
            logger.error("MultiModal API timeout")
            raise Exception("MultiModal API request timed out")
        except Exception as e:
            logger.error(f"MultiModal API error: {e}")
            raise
    
    def extract_image_url(self, response: Dict) -> Optional[str]:
        """
        Extract image URL from MultiModal API response
        
        Args:
            response: API response dictionary
            
        Returns:
            Image URL or None if extraction fails
        """
        try:
            # Navigate the response structure
            output = response.get('output', {})
            choices = output.get('choices', [])
            
            if not choices:
                logger.error("No choices in API response")
                return None
            
            message = choices[0].get('message', {})
            content = message.get('content', [])
            
            if not content:
                logger.error("No content in API response")
                return None
            
            # Find the image URL in content
            for item in content:
                if 'image' in item:
                    return item['image']
            
            logger.error("No image URL found in response")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract image URL: {e}")
            return None


class TextClient:
    """Async client for DashScope Text API (Qwen Turbo for prompt enhancement)"""
    
    def __init__(self):
        """Initialize Text client"""
        self.api_key = config.DASHSCOPE_API_KEY
        self.base_url = config.DASHSCOPE_BASE_URL
        self.model = config.QWEN_TEXT_MODEL
        self.timeout = config.API_TIMEOUT
        
        # Construct the full API URL for text generation
        self.api_url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        logger.info(f"TextClient initialized with model: {self.model}")
    
    async def enhance_prompt(self, original_prompt: str) -> str:
        """
        Enhance prompt for K12 classroom use using Qwen Turbo
        
        Args:
            original_prompt: Original user prompt
            
        Returns:
            Enhanced prompt or original if enhancement fails
        """
        try:
            enhancement_prompt = f"""You are an expert K12 teacher and educational content creator specializing in creating engaging visual materials for classroom instruction.

Your task is to transform a simple image generation prompt into a detailed, educationally-focused description that will generate high-quality images perfect for K12 classroom use.

Original prompt: "{original_prompt}"

IMPORTANT SAFETY GUIDELINES - STRICTLY FOLLOW THESE RULES:
- ONLY create prompts for educational, classroom-appropriate content
- AVOID any controversial, political, religious, or sensitive topics
- NO violence, weapons, or harmful content
- NO adult content, explicit material, or inappropriate themes
- NO copyrighted characters, brands, or trademarked content
- NO content that could offend cultural or religious groups
- FOCUS on academic subjects, nature, science, art, and positive learning themes
- CRITICAL: The final generated image should contain NO text, words, letters, numbers, or written characters of any kind
- NO signs, labels, banners, posters with text, or any written content should appear in the image
- NO Chinese characters, English text, or any language symbols should be rendered
- Focus on visual elements only: objects, scenes, colors, shapes, and visual concepts
- If the prompt mentions text elements, describe the visual appearance without including the actual text content

Please enhance this prompt by following these educational guidelines:

1. **Educational Context**: Add subject-specific educational elements (science, math, history, language arts, etc.) that relate to the prompt
2. **Age-Appropriate Content**: Ensure the description is suitable for K12 students (elementary, middle, or high school level)
3. **Visual Learning Elements**: Include specific visual details that support learning objectives and make concepts clearer
4. **Classroom Environment**: Add context that makes the image feel like it belongs in an educational setting
5. **Engagement Factors**: Include elements that would capture student attention and interest
6. **Cultural Sensitivity**: Ensure the description is inclusive and appropriate for diverse classrooms
7. **Learning Objectives**: Structure the description to support specific educational outcomes

SAFE CONTENT CATEGORIES TO FOCUS ON:
- Natural science and biology (animals, plants, ecosystems)
- Mathematics and geometry concepts
- Art and creative expression
- Geography and landscapes
- Historical architecture and cultural artifacts
- Technology and innovation
- Environmental conservation
- Space and astronomy
- Weather and climate
- Food and nutrition (healthy choices)

Keep the enhanced prompt under 250 words and make it specific, descriptive, and educationally valuable.

Enhanced prompt:"""
            
            payload = {
                "model": self.model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": enhancement_prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": 300,
                    "temperature": 0.7,
                    "top_p": 0.8
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info("=" * 80)
            logger.info("PROMPT ENHANCEMENT - Qwen Turbo")
            logger.info("=" * 80)
            logger.info(f"Original Prompt: {original_prompt}")
            logger.info(f"Original Length: {len(original_prompt)} chars")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract the enhanced text
                        output = data.get('output', {})
                        text = output.get('text', '').strip()
                        
                        if text:
                            logger.info("-" * 80)
                            logger.info(f"Enhanced Prompt: {text}")
                            logger.info(f"Enhanced Length: {len(text)} chars")
                            logger.info("=" * 80)
                            return text
                        else:
                            logger.warning("Empty response from Qwen Turbo, using original prompt")
                            logger.info("=" * 80)
                            return original_prompt
                    else:
                        error_text = await response.text()
                        logger.warning(f"Qwen Turbo API error {response.status}: {error_text}, using original prompt")
                        logger.info("=" * 80)
                        return original_prompt
                        
        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            logger.info("Falling back to original prompt")
            logger.info("=" * 80)
            return original_prompt


# ============================================================================
# GLOBAL CLIENT INSTANCES
# ============================================================================

# Global client instances
try:
    multimodal_client = MultiModalClient()
    text_client = TextClient()
    logger.info("MultiModal and Text clients initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize clients: {e}")
    multimodal_client = None
    text_client = None

