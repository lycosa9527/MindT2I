"""
Video Generation Client for MindT2I
====================================

Client for DashScope VideoSynthesis API with async task polling
Supports wan2.5-t2v-preview (with audio) and wan2.2-t2v-plus models

Uses async_call + wait pattern for better performance
"""

import logging
import asyncio
from typing import Dict, Optional
import dashscope
from dashscope import VideoSynthesis
from http import HTTPStatus

from config.settings import config

logger = logging.getLogger(__name__)


class VideoClient:
    """Client for DashScope Video Synthesis API with async support"""
    
    # Resolution mapping for better UX
    SIZE_MAPPING = {
        # 720P options (default)
        "1280*720": "1280*720",    # 16:9 landscape
        "720*1280": "720*1280",    # 9:16 portrait
        "960*960": "960*960",      # 1:1 square
        "1088*832": "1088*832",    # 4:3
        "832*1088": "832*1088",    # 3:4
        
        # 1080P options
        "1920*1080": "1920*1080",  # 16:9 landscape
        "1080*1920": "1080*1920",  # 9:16 portrait
        "1440*1440": "1440*1440",  # 1:1 square
        "1632*1248": "1632*1248",  # 4:3
        "1248*1632": "1248*1632",  # 3:4
        
        # 480P options
        "832*480": "832*480",      # 16:9 landscape
        "480*832": "480*832",      # 9:16 portrait
        "624*624": "624*624",      # 1:1 square
    }
    
    def __init__(self):
        """Initialize Video client"""
        self.api_key = config.DASHSCOPE_API_KEY
        self.model = config.VIDEO_MODEL or "wan2.5-t2v-preview"
        
        # Set DashScope base URL
        dashscope.base_http_api_url = config.DASHSCOPE_BASE_URL
        
        logger.info(f"VideoClient initialized with model: {self.model}")
    
    def _normalize_size(self, size: str) -> str:
        """
        Normalize size to valid video resolution
        
        Args:
            size: Input size (e.g., "1328*1328", "1664*928")
            
        Returns:
            Valid video size for the API
        """
        # If already a valid video size, return as is
        if size in self.SIZE_MAPPING:
            return size
        
        # Parse dimensions
        try:
            width, height = map(int, size.split('*'))
            aspect_ratio = width / height
            
            # Map to closest video resolution based on aspect ratio
            if aspect_ratio > 1.5:  # Landscape 16:9
                return "1920*1080"  # Default 1080P landscape
            elif aspect_ratio < 0.7:  # Portrait 9:16
                return "1080*1920"  # Default 1080P portrait
            else:  # Square-ish
                return "1440*1440"  # Default 1080P square
                
        except Exception as e:
            logger.warning(f"Failed to parse size {size}, using default: {e}")
            return config.VIDEO_DEFAULT_SIZE  # Use config default
    
    async def generate_video(
        self,
        prompt: str,
        size: Optional[str] = None,
        duration: Optional[int] = None,
        prompt_extend: Optional[bool] = None,
        watermark: Optional[bool] = None,
        audio: Optional[bool] = None,
        audio_url: Optional[str] = None,
        negative_prompt: str = "",
        seed: Optional[int] = None
    ) -> str:
        """
        Generate video using DashScope VideoSynthesis API (Async Task Pattern)
        
        Uses async_call + wait pattern:
        1. async_call() - Creates task, returns immediately with task_id
        2. wait() - Polls task status until completion (SUCCEEDED/FAILED)
        
        Args:
            prompt: Text description for video generation
            size: Video resolution (None = use VIDEO_DEFAULT_SIZE from config)
                   Available: 480P (832*480), 720P (1280*720), 1080P (1920*1080)
            duration: Video duration in seconds (None = use VIDEO_DEFAULT_DURATION)
                      Options: 5 or 10 (only wan2.5-t2v-preview supports 10s)
            prompt_extend: Enable intelligent prompt rewriting (None = use VIDEO_PROMPT_EXTEND)
            watermark: Add "AI生成" watermark to video (None = use VIDEO_WATERMARK)
            audio: Auto-generate audio (None = use VIDEO_AUDIO, wan2.5 only)
            audio_url: Custom audio file URL (wan2.5 only)
            negative_prompt: Reverse prompt to exclude unwanted content
            seed: Random seed for reproducibility
            
        Returns:
            Video URL (valid for 24 hours)
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Apply defaults from config if not provided
            if size is None:
                size = config.VIDEO_DEFAULT_SIZE
            if duration is None:
                duration = config.VIDEO_DEFAULT_DURATION
            if prompt_extend is None:
                prompt_extend = config.VIDEO_PROMPT_EXTEND
            if watermark is None:
                watermark = config.VIDEO_WATERMARK
            if audio is None:
                audio = config.VIDEO_AUDIO
            
            # Normalize size
            normalized_size = self._normalize_size(size)
            logger.info("=" * 80)
            logger.info("VIDEO GENERATION - wan2.5-t2v-preview")
            logger.info("=" * 80)
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Size: {normalized_size}")
            logger.info(f"Duration: {duration}s")
            logger.info(f"Prompt Extend: {prompt_extend}")
            logger.info(f"Watermark: {watermark}")
            logger.info(f"Audio: {audio}")
            if audio_url:
                logger.info(f"Audio URL: {audio_url}")
            if negative_prompt:
                logger.info(f"Negative Prompt: {negative_prompt}")
            logger.info("-" * 80)
            
            # Step 1: Create async task (returns immediately with task_id)
            loop = asyncio.get_running_loop()
            task_response = await loop.run_in_executor(
                None,
                lambda: VideoSynthesis.async_call(
                    api_key=self.api_key,
                    model=self.model,
                    prompt=prompt,
                    size=normalized_size,
                    prompt_extend=prompt_extend,
                    watermark=watermark,
                    negative_prompt=negative_prompt,
                    seed=seed,
                    **self._get_model_specific_params(duration, audio, audio_url)
                )
            )
            
            # Check if task creation succeeded
            if task_response.status_code != HTTPStatus.OK:
                error_msg = (f"Failed to create video task - Status: {task_response.status_code}, "
                           f"Code: {task_response.code}, Message: {task_response.message}")
                logger.error(error_msg)
                raise Exception(error_msg)
            
            task_id = task_response.output.task_id
            logger.info(f"✅ Task created successfully: {task_id}")
            logger.info(f"⏳ Waiting for video generation (this may take 1-5 minutes)...")
            
            # Step 2: Wait for task completion (polls automatically)
            final_response = await loop.run_in_executor(
                None,
                lambda: VideoSynthesis.wait(task_response)
            )
            
            # Check final response
            if final_response.status_code == HTTPStatus.OK:
                video_url = final_response.output.video_url
                task_status = final_response.output.task_status
                
                logger.info("Video generation completed successfully!")
                logger.info(f"Status: {task_status}")
                logger.info(f"Video URL: {video_url}")
                logger.info(f"Duration: {duration}s")
                logger.info(f"Size: {normalized_size}")
                
                # Log API-level prompt enhancement if available
                if hasattr(final_response.output, 'actual_prompt') and final_response.output.actual_prompt:
                    logger.info("-" * 80)
                    logger.info("API-Level Prompt Enhancement (wan2.5 internal):")
                    logger.info(f"{final_response.output.actual_prompt}")
                
                logger.info("=" * 80)
                return video_url
            else:
                error_msg = (f"Video generation failed - Status: {final_response.status_code}, "
                           f"Code: {final_response.code}, Message: {final_response.message}")
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"VideoSynthesis API error: {e}")
            raise
    
    def _get_model_specific_params(
        self,
        duration: int,
        audio: bool,
        audio_url: Optional[str]
    ) -> Dict:
        """
        Get model-specific parameters
        
        Args:
            duration: Video duration
            audio: Auto-generate audio
            audio_url: Custom audio URL
            
        Returns:
            Dict of model-specific parameters
        """
        params = {}
        
        # wan2.5 supports duration and audio
        if self.model == "wan2.5-t2v-preview":
            params['duration'] = duration
            if audio_url:
                params['audio_url'] = audio_url
            else:
                params['audio'] = audio
        
        return params


# Global instance
video_client = VideoClient()

