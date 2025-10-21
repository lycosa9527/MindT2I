"""
Unified Generation Service for MindT2I
=======================================

Intelligent service that uses ReAct agent to route between
image and video generation based on user intent.
"""

import os
import uuid
import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, Literal
from pathlib import Path

from config.settings import config
from agents.intent_agent import intent_agent
from clients.video import video_client
from services.image_service import image_service

logger = logging.getLogger(__name__)

# Semaphores for limiting concurrent operations
VIDEO_GENERATION_SEMAPHORE = asyncio.Semaphore(20)  # Max 20 concurrent video generations
VIDEO_DOWNLOAD_SEMAPHORE = asyncio.Semaphore(10)    # Max 10 concurrent downloads


class UnifiedGenerationService:
    """Service for intelligent image/video generation with ReAct agent"""
    
    def __init__(self):
        """Initialize unified generation service"""
        self.temp_folder = Path(config.TEMP_FOLDER)
        self.temp_folder.mkdir(exist_ok=True)
        
        # Create separate folders for images and videos
        self.temp_images_folder = self.temp_folder
        self.temp_videos_folder = Path("temp_videos")
        self.temp_videos_folder.mkdir(exist_ok=True)
        
        logger.info(f"UnifiedGenerationService initialized")
        logger.info(f"  Images: {self.temp_images_folder}")
        logger.info(f"  Videos: {self.temp_videos_folder}")
    
    async def generate(
        self,
        prompt: str,
        size: str = "1328*1328",
        watermark: bool = False,
        negative_prompt: str = "",
        prompt_extend: bool = True,
        force_type: Literal["image", "video", "auto"] = "auto"
    ) -> Dict:
        """
        Generate image or video based on intelligent intent detection.
        
        Args:
            prompt: User's text prompt
            size: Size for image/video
            watermark: Whether to add watermark (image only)
            negative_prompt: Negative prompt (image only)
            prompt_extend: Whether to extend prompt
            force_type: Force a specific type or use "auto" for intelligent detection
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Step 1: Analyze intent using ReAct agent
            if force_type == "auto":
                logger.info("Using ReAct agent to analyze intent...")
                intent_result = await intent_agent.analyze_intent(prompt)
                
                media_type = intent_result["intent"]
                enhanced_prompt = intent_result["enhanced_prompt"]
                confidence = intent_result["confidence"]
                reasoning = intent_result["reasoning"]
                
                logger.info(f"ReAct decision: {media_type} (confidence: {confidence})")
                logger.debug(f"Reasoning: {reasoning}")
            else:
                media_type = force_type
                enhanced_prompt = prompt
                confidence = 1.0
                reasoning = f"Forced to {force_type} by user"
                intent_result = {
                    "intent": media_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "enhanced_prompt": enhanced_prompt
                }
            
            # Step 2: Route to appropriate generation method
            if media_type == "video":
                result = await self._generate_video(
                    prompt=enhanced_prompt,
                    size=size,
                    intent_result=intent_result,
                    watermark=watermark,
                    negative_prompt=negative_prompt,
                    prompt_extend=prompt_extend
                )
            else:  # image
                result = await self._generate_image(
                    enhanced_prompt,
                    size,
                    watermark,
                    negative_prompt,
                    prompt_extend,
                    intent_result
                )
            
            # Add intent information to result
            result["intent_analysis"] = {
                "detected_type": media_type,
                "confidence": confidence,
                "reasoning": reasoning,
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Unified generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_image(
        self,
        prompt: str,
        size: str,
        watermark: bool,
        negative_prompt: str,
        prompt_extend: bool,
        intent_result: Dict
    ) -> Dict:
        """Generate image using image_service (includes Qwen Turbo enhancement)"""
        logger.info("Routing to image generation (with Qwen Turbo enhancement)...")
        
        # Use image_service which includes Qwen Turbo prompt enhancement
        result = await image_service.generate_image(
            prompt=prompt,
            size=size,
            watermark=watermark,
            negative_prompt=negative_prompt,
            prompt_extend=prompt_extend
        )
        
        # image_service returns a complete result dict
        # Add the type field for unified response format
        result['type'] = 'image'
        result['url'] = result['image_url']
        result['markdown'] = result['markdown_image']
        
        return result
    
    async def _generate_video(
        self,
        prompt: str,
        size: str,
        intent_result: Dict,
        watermark: bool = False,
        negative_prompt: str = "",
        prompt_extend: bool = True
    ) -> Dict:
        """
        Generate video with new DashScope API parameters.
        
        Uses semaphore to limit concurrent video generations.
        
        Args:
            prompt: User's text prompt
            size: Video size
            intent_result: Intent detection result from agent
            watermark: Whether to add watermark
            negative_prompt: Negative prompt for video
            prompt_extend: Whether to extend prompt
            
        Returns:
            Dict with video generation results
        """
        # Use semaphore to limit concurrent video generations
        async with VIDEO_GENERATION_SEMAPHORE:
            logger.info("Routing to video generation...")
            logger.info(f"Active video generations: {20 - VIDEO_GENERATION_SEMAPHORE._value}/20")
            
            # Normalize size for video (convert to video-friendly format)
            video_size = self._normalize_video_size(size)
            
            # Generate video with parameters (using config defaults if not specified)
            dashscope_video_url = await video_client.generate_video(
                prompt=prompt,
                size=video_size,
                duration=None,  # Use VIDEO_DEFAULT_DURATION from config
                prompt_extend=prompt_extend if prompt_extend is not None else None,
                watermark=watermark if watermark is not None else None,
                audio=None,  # Use VIDEO_AUDIO from config
                negative_prompt=negative_prompt
            )
            
            if not dashscope_video_url:
                raise Exception("Failed to generate video")
            
            logger.info(f"Video generated, downloading from DashScope...")
            
            # Download and save video to temp folder
            filename = await self._download_and_save_video(dashscope_video_url)
            
            # Construct local server URL
            server_url = config.SERVER_URL
            local_video_url = f"{server_url}/temp_videos/{filename}"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # User-friendly message for video download
            plain_text = f"Please copy the link to your web browser to download the video, video URL: {dashscope_video_url}"
            
            return {
                'success': True,
                'type': 'video',
                'url': dashscope_video_url,  # DashScope URL (valid 24h)
                'local_url': local_video_url,  # Local server URL (permanent)
                'filename': filename,
                'text': plain_text,  # User-friendly download message
                'message': plain_text,  # Alias for compatibility
                'markdown': f'<video src="{local_video_url}" controls></video>',  # Use local URL for web display
                'size': video_size,
                'duration': config.VIDEO_DEFAULT_DURATION,  # From config
                'timestamp': timestamp,
                'request_id': str(uuid.uuid4()),
                'has_audio': config.VIDEO_AUDIO,  # From config
                'model': video_client.model,
                'intent_analysis': {
                    'detected_type': intent_result.get('intent'),
                    'confidence': intent_result.get('confidence'),
                    'reasoning': intent_result.get('reasoning')
                }
            }
    
    def _normalize_video_size(self, size: str) -> str:
        """
        Convert image size to video-friendly size.
        
        Args:
            size: Image size (e.g., "1328*1328")
            
        Returns:
            Video size (e.g., "1920*1080" for 1080P)
        """
        # Map common image sizes to video sizes (1080P defaults)
        size_map = {
            "1328*1328": "1920*1080",  # Square to 16:9 1080P
            "1664*928": "1920*1080",   # 16:9 landscape to 1080P
            "1472*1140": "1920*1080",  # 4:3 to 16:9 1080P
            "1140*1472": "1080*1920",  # 3:4 to 9:16 1080P portrait
            "928*1664": "1080*1920"    # 9:16 portrait to 1080P
        }
        
        return size_map.get(size, "1920*1080")  # Default to 1080P
    
    async def _download_and_save_video(self, video_url: str) -> str:
        """
        Download video from DashScope URL and save to temp folder.
        
        Uses semaphore to limit concurrent downloads and prevent memory exhaustion.
        """
        # Use semaphore to limit concurrent downloads
        async with VIDEO_DOWNLOAD_SEMAPHORE:
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"generated_{timestamp}_{unique_id}.mp4"
                
                logger.info(f"Downloading video: {filename}")
                logger.info(f"Active downloads: {10 - VIDEO_DOWNLOAD_SEMAPHORE._value}/10")
                
                # Download video with streaming (videos can be large)
                timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout for video download
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(video_url) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download video: HTTP {response.status}")
                        
                        # Save to temp folder with streaming (chunk by chunk)
                        file_path = self.temp_videos_folder / filename
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                
                logger.info(f"✅ Video saved successfully: {filename}")
                return filename
                
            except Exception as e:
                logger.error(f"Failed to download and save video: {e}")
                raise


# Global service instance
unified_service = UnifiedGenerationService()

