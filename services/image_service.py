"""
Image Generation Service for MindT2I
====================================

Business logic for image generation using DashScope MultiModal API.
"""

import os
import uuid
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

from config.settings import config
from clients.image import image_client
from clients.multimodal import text_client

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for handling image generation requests"""
    
    def __init__(self):
        """Initialize image generation service"""
        self.temp_folder = Path(config.TEMP_FOLDER)
        self.temp_folder.mkdir(exist_ok=True)
        logger.info(f"ImageGenerationService initialized with temp folder: {self.temp_folder}")
    
    def validate_image_size(self, size: str) -> str:
        """
        Validate and normalize image size
        
        Args:
            size: Image size string (e.g., "1328*1328")
            
        Returns:
            Validated size string
        """
        valid_sizes = {
            "1664*928": "1664*928",   # 16:9
            "1472*1140": "1472*1140", # 4:3
            "1328*1328": "1328*1328", # 1:1 (default)
            "1140*1472": "1140*1472", # 3:4
            "928*1664": "928*1664"    # 9:16
        }
        return valid_sizes.get(size, "1328*1328")
    
    def validate_prompt(self, prompt: str) -> Tuple[bool, Optional[str]]:
        """
        Validate prompt content
        
        Args:
            prompt: User prompt to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not prompt or len(prompt.strip()) < config.MIN_PROMPT_LENGTH:
            return False, f"Prompt is too short (min {config.MIN_PROMPT_LENGTH} characters)"
        
        if len(prompt) > config.MAX_PROMPT_LENGTH:
            return False, f"Prompt is too long (max {config.MAX_PROMPT_LENGTH} characters)"
        
        return True, None
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1328*1328",
        watermark: bool = False,
        negative_prompt: str = "",
        prompt_extend: bool = True
    ) -> Dict:
        """
        Generate image from prompt
        
        Args:
            prompt: Text description for image generation
            size: Image size
            watermark: Whether to add watermark
            negative_prompt: Negative prompt
            prompt_extend: Whether to extend prompt
            
        Returns:
            Dictionary with generation results
            
        Raises:
            Exception: If generation fails
        """
        # Validate prompt
        is_valid, error_msg = self.validate_prompt(prompt)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate and normalize size
        size = self.validate_image_size(size)
        
        # Store original prompt
        original_prompt = prompt
        
        # Enhance prompt if enabled
        enhanced_prompt = None
        if config.ENABLE_PROMPT_ENHANCEMENT:
            try:
                logger.info(f"Prompt enhancement enabled, sending to Qwen Turbo...")
                enhanced_prompt = await text_client.enhance_prompt(original_prompt)
                prompt = enhanced_prompt
                logger.info(f"Prompt enhancement successful")
            except Exception as e:
                logger.error(f"Prompt enhancement failed: {e}")
                logger.warning(f"Using original prompt without enhancement")
                prompt = original_prompt
        else:
            logger.info(f"Prompt enhancement disabled (ENABLE_PROMPT_ENHANCEMENT=false)")
        
        # Generate image using new ImageSynthesis client (async task-based)
        try:
            # Use final enhanced prompt (or original if enhancement failed)
            final_prompt = enhanced_prompt if enhanced_prompt else original_prompt
            
            image_url = await image_client.generate_image(
                prompt=final_prompt,
                size=size,
                n=1,
                prompt_extend=False,  # Already enhanced by us
                watermark=watermark,
                negative_prompt=negative_prompt
            )
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
        
        if not image_url:
            raise Exception("Failed to generate image")
        
        # Download and save image
        filename = await self.download_and_save_image(image_url)
        
        # Construct full image URL
        server_url = config.SERVER_URL
        full_image_url = f"{server_url}/temp_images/{filename}"
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create response
        result = {
            'success': True,
            'image_url': full_image_url,
            'markdown_image': f"![]({full_image_url})",
            'message': 'Image generated successfully',
            'filename': filename,
            'size': size,
            'prompt_enhanced': config.ENABLE_PROMPT_ENHANCEMENT and enhanced_prompt is not None,
            'original_prompt': original_prompt,
            'enhanced_prompt': enhanced_prompt if config.ENABLE_PROMPT_ENHANCEMENT else None,
            'timestamp': timestamp,
            'request_id': str(uuid.uuid4())
        }
        
        logger.info(f"Image generation completed - Filename: {filename}, Size: {size}")
        return result
    
    async def download_and_save_image(self, image_url: str) -> str:
        """
        Download image from URL and save to temp folder
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Filename of saved image
            
        Raises:
            Exception: If download or save fails
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"generated_{timestamp}_{unique_id}.jpg"
            
            # Download image
            timeout = aiohttp.ClientTimeout(total=config.IMAGE_DOWNLOAD_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    image_data = await response.read()
            
            # Save to temp folder
            file_path = self.temp_folder / filename
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            logger.debug(f"Image saved successfully: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to download and save image: {e}")
            raise
    
    def cleanup_old_images(self, max_age_hours: int = 24):
        """
        Clean up old images from temp folder
        
        Args:
            max_age_hours: Maximum age of images in hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 60 * 60
            
            count = 0
            for file_path in self.temp_folder.glob("generated_*.jpg"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} old image(s)")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old images: {e}")


# Global service instance
image_service = ImageGenerationService()

