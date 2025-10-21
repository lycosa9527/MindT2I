"""
Image Generation Client for MindT2I
====================================

Client for DashScope ImageSynthesis API with async task polling
Supports wan2.2-t2i-flash and other text-to-image models

Uses async_call + wait pattern (same as video generation)
"""

import logging
import asyncio
from typing import Dict, Optional
import dashscope
from dashscope import ImageSynthesis
from http import HTTPStatus

from config.settings import config

logger = logging.getLogger(__name__)


class ImageClient:
    """Client for DashScope Image Synthesis API with async support"""
    
    # Resolution mapping for better UX
    SIZE_MAPPING = {
        # wan2.5-t2i-preview sizes (recommended)
        "1280*1280": "1280*1280",  # 1:1 square (default for wan2.5)
        "1200*800": "1200*800",    # 3:2 landscape
        "800*1200": "800*1200",    # 2:3 portrait
        "1280*960": "1280*960",    # 4:3 landscape
        "960*1280": "960*1280",    # 3:4 portrait
        "1280*720": "1280*720",    # 16:9 landscape
        "720*1280": "720*1280",    # 9:16 portrait
        "1344*576": "1344*576",    # 21:9 ultra-wide
        
        # wan2.2 sizes (backward compatibility)
        "1024*1024": "1024*1024",  # 1:1 square (wan2.2 default)
        
        # Legacy sizes (for compatibility)
        "1328*1328": "1280*1280",  # Map to standard square
        "1664*928": "1280*720",    # Map to 16:9
        "928*1664": "720*1280",    # Map to 9:16
    }
    
    # Model-specific default prompt_extend settings
    MODEL_DEFAULTS = {
        "wan2.5-t2i-preview": {
            "prompt_extend": True,   # Override to true for better quality
            "max_prompt_length": 2000,
            "default_size": "1280*960"  # 4:3 aspect ratio
        },
        "wan2.2-t2i-flash": {
            "prompt_extend": True,   # wan2.2 default
            "max_prompt_length": 800,
            "default_size": "1024*1024"
        }
    }
    
    def __init__(self):
        """Initialize Image client"""
        self.api_key = config.DASHSCOPE_API_KEY
        self.model = config.IMAGE_MODEL or "wan2.5-t2i-preview"
        
        # Set DashScope base URL
        dashscope.base_http_api_url = config.DASHSCOPE_BASE_URL
        
        # Get model-specific defaults
        self.model_config = self.MODEL_DEFAULTS.get(
            self.model, 
            self.MODEL_DEFAULTS["wan2.5-t2i-preview"]
        )
        
        logger.info(f"ImageClient initialized with model: {self.model}")
        logger.info(f"  Max prompt length: {self.model_config['max_prompt_length']} chars")
        logger.info(f"  Default size: {self.model_config['default_size']}")
    
    def _normalize_size(self, size: str) -> str:
        """
        Normalize size to valid image resolution
        
        Args:
            size: Input size (e.g., "1328*1328", "1024*1024")
            
        Returns:
            Valid image size for the API
        """
        # If already a valid size, return as is
        if size in self.SIZE_MAPPING:
            return self.SIZE_MAPPING[size]
        
        # Parse dimensions
        try:
            width, height = map(int, size.split('*'))
            aspect_ratio = width / height
            
            # Map to closest standard resolution
            if aspect_ratio > 1.5:  # Landscape 16:9
                return "1280*720"
            elif aspect_ratio < 0.7:  # Portrait 9:16
                return "720*1280"
            else:  # Square-ish
                return "1024*1024"
                
        except Exception as e:
            logger.warning(f"Failed to parse size {size}, using default: {e}")
            # Use model-specific default
            if hasattr(config, 'IMAGE_DEFAULT_SIZE'):
                return config.IMAGE_DEFAULT_SIZE
            return self.model_config['default_size']
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        n: int = 1,
        prompt_extend: Optional[bool] = None,
        watermark: Optional[bool] = None,
        negative_prompt: str = "",
        seed: Optional[int] = None
    ) -> str:
        """
        Generate image using DashScope ImageSynthesis API (Async Task Pattern)
        
        Uses async_call + wait pattern (same as video):
        1. async_call() - Creates task, returns immediately with task_id
        2. wait() - Polls task status until completion (SUCCEEDED/FAILED)
        
        Args:
            prompt: Text description for image generation
            size: Image resolution (None = use config default)
                   Available: 1024*1024, 1280*720, 720*1280
            n: Number of images to generate (default: 1)
            prompt_extend: Enable intelligent prompt rewriting (None = use config)
            watermark: Add watermark to image (None = use config)
            negative_prompt: Reverse prompt to exclude unwanted content
            seed: Random seed for reproducibility
            
        Returns:
            Image URL (valid for 24 hours)
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Apply defaults from config if not provided
            if size is None:
                size = getattr(config, 'IMAGE_DEFAULT_SIZE', self.model_config['default_size'])
            if prompt_extend is None:
                # Use model-specific default if not set in config
                prompt_extend = getattr(config, 'IMAGE_PROMPT_EXTEND', self.model_config['prompt_extend'])
            if watermark is None:
                watermark = getattr(config, 'IMAGE_WATERMARK', False)
            
            # Normalize size
            normalized_size = self._normalize_size(size)
            logger.info("=" * 80)
            logger.info("IMAGE GENERATION - wan2.5-t2i-preview")
            logger.info("=" * 80)
            logger.info(f"Final Prompt (sent to API): {prompt}")
            logger.info(f"Size: {normalized_size}")
            logger.info(f"Count: {n}")
            logger.info(f"Prompt Extend (API-level): {prompt_extend}")
            logger.info(f"Watermark: {watermark}")
            if negative_prompt:
                logger.info(f"Negative Prompt: {negative_prompt}")
            logger.info("-" * 80)
            
            # Build parameters
            params = {
                'api_key': self.api_key,
                'model': self.model,
                'prompt': prompt,
                'n': n,
                'size': normalized_size
            }
            
            # Add optional parameters
            if negative_prompt:
                params['negative_prompt'] = negative_prompt
            if seed is not None:
                params['seed'] = seed
            
            # Step 1: Create async task (returns immediately with task_id)
            loop = asyncio.get_running_loop()
            task_response = await loop.run_in_executor(
                None,
                lambda: ImageSynthesis.async_call(**params)
            )
            
            # Check if task creation succeeded
            if task_response.status_code != HTTPStatus.OK:
                error_msg = (f"Failed to create image task - Status: {task_response.status_code}, "
                           f"Code: {task_response.code}, Message: {task_response.message}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            task_id = task_response.output.task_id
            logger.info(f"✅ Task created successfully: {task_id}")
            logger.info(f"⏳ Waiting for image generation (typically 10-20 seconds)...")
            
            # Step 2: Wait for task completion (polls automatically)
            final_response = await loop.run_in_executor(
                None,
                lambda: ImageSynthesis.wait(task_response)
            )
            
            # Check final response
            if final_response.status_code == HTTPStatus.OK:
                results = final_response.output.results
                if not results or len(results) == 0:
                    raise Exception("No images generated")
                
                image_url = results[0].url
                task_status = final_response.output.task_status
                
                logger.info("Image generation completed successfully!")
                logger.info(f"Status: {task_status}")
                logger.info(f"Image URL: {image_url}")
                logger.info(f"Size: {normalized_size}")
                
                # Log API-level prompt enhancement if available
                if hasattr(results[0], 'actual_prompt') and results[0].actual_prompt:
                    logger.info("-" * 80)
                    logger.info("API-Level Prompt Enhancement (wan2.5 internal):")
                    logger.info(f"{results[0].actual_prompt}")
                
                logger.info("=" * 80)
                return image_url
            else:
                error_msg = (f"Image generation failed - Status: {final_response.status_code}, "
                           f"Code: {final_response.code}, Message: {final_response.message}")
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"ImageSynthesis API error: {e}")
            raise


# Global instance
image_client = ImageClient()

