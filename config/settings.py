"""
MindT2I Configuration Module
=============================

Centralized configuration management for the MindT2I application.
Handles environment variable loading, validation, and provides a clean interface
for accessing configuration values throughout the application.

Features:
- Dynamic environment variable loading with .env support
- Property-based configuration access for real-time updates
- Comprehensive validation for required and optional settings
- Default values for all configuration options
- Support for DashScope API configuration
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Centralized configuration management for MindT2I application.
    """
    def __init__(self):
        self._cache = {}
        self._cache_timestamp = 0
        self._cache_duration = 30  # Cache for 30 seconds
        self._version = None  # Cached version
    
    @property
    def VERSION(self) -> str:
        """Application version (Semantic Versioning) - read from VERSION file"""
        if self._version is None:
            try:
                version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
                with open(version_file, 'r', encoding='utf-8') as f:
                    self._version = f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to read VERSION file: {e}, using fallback")
                self._version = "2.2.0"  # Fallback version
        return self._version
    
    def _get_cached_value(self, key: str, default=None):
        import time
        current_time = time.time()
        if current_time - self._cache_timestamp > self._cache_duration:
            self._cache.clear()
            self._cache_timestamp = current_time
        if key not in self._cache:
            self._cache[key] = os.environ.get(key, default)
        return self._cache[key]
    
    # ============================================================================
    # DASHSCOPE API CONFIGURATION
    # ============================================================================
    
    @property
    def DASHSCOPE_API_KEY(self):
        api_key = self._get_cached_value('DASHSCOPE_API_KEY')
        if not api_key or not isinstance(api_key, str):
            logger.warning("Invalid or missing DASHSCOPE_API_KEY")
            return None
        return api_key.strip()
    
    @property
    def DASHSCOPE_BASE_URL(self):
        """DashScope base API URL"""
        return self._get_cached_value('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/api/v1')
    
    @property
    def QWEN_IMAGE_MODEL(self):
        """Qwen multimodal image generation model (legacy)"""
        return self._get_cached_value('QWEN_IMAGE_MODEL', 'qwen-image-plus')
    
    @property
    def IMAGE_MODEL(self):
        """DashScope image generation model"""
        return self._get_cached_value('IMAGE_MODEL', 'wan2.5-t2i-preview')
    
    @property
    def QWEN_TEXT_MODEL(self):
        """Qwen text model for prompt enhancement"""
        return self._get_cached_value('QWEN_TEXT_MODEL', 'qwen-turbo')
    
    @property
    def VIDEO_MODEL(self):
        """DashScope video generation model"""
        return self._get_cached_value('VIDEO_MODEL', 'wan2.5-t2v-preview')
    
    # Image Generation Settings
    @property
    def IMAGE_DEFAULT_SIZE(self):
        """Default image resolution (e.g., 1280*960, 1280*1280)"""
        return self._get_cached_value('IMAGE_DEFAULT_SIZE', '1280*960')
    
    @property
    def IMAGE_PROMPT_EXTEND(self):
        """Enable prompt enhancement for images by default"""
        # Default to true for better prompt quality
        value = self._get_cached_value('IMAGE_PROMPT_EXTEND', 'true')
        if not value:
            return None  # Let ImageClient use model-specific default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @property
    def IMAGE_WATERMARK(self):
        """Add watermark to images by default"""
        value = self._get_cached_value('IMAGE_WATERMARK', 'false')
        return value.lower() in ('true', '1', 'yes', 'on')
    
    # Video Generation Settings
    @property
    def VIDEO_DEFAULT_SIZE(self):
        """Default video resolution (e.g., 1920*1080, 1280*720)"""
        return self._get_cached_value('VIDEO_DEFAULT_SIZE', '1920*1080')
    
    @property
    def VIDEO_DEFAULT_DURATION(self):
        """Default video duration in seconds (5 or 10)"""
        value = self._get_cached_value('VIDEO_DEFAULT_DURATION', '10')
        return int(value)
    
    @property
    def VIDEO_PROMPT_EXTEND(self):
        """Enable prompt enhancement for videos by default"""
        value = self._get_cached_value('VIDEO_PROMPT_EXTEND', 'true')
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @property
    def VIDEO_WATERMARK(self):
        """Add watermark to videos by default"""
        value = self._get_cached_value('VIDEO_WATERMARK', 'false')
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @property
    def VIDEO_AUDIO(self):
        """Enable audio for videos by default (wan2.5 only)"""
        value = self._get_cached_value('VIDEO_AUDIO', 'true')
        return value.lower() in ('true', '1', 'yes', 'on')
    
    # ============================================================================
    # SERVER CONFIGURATION
    # ============================================================================
    
    @property
    def HOST(self):
        """FastAPI application host address"""
        return self._get_cached_value('HOST', '0.0.0.0')
    
    @property
    def PORT(self):
        """FastAPI application port number"""
        try:
            val = int(self._get_cached_value('PORT', '9528'))
            if not (1 <= val <= 65535):
                logger.warning(f"PORT {val} out of range, using 9528")
                return 9528
            return val
        except (ValueError, TypeError):
            logger.warning("Invalid PORT value, using 9528")
            return 9528
    
    @property
    def SERVER_URL(self):
        """Get the server URL for image serving"""
        host = self.SERVER_HOST
        port = self.PORT
        return f"http://{host}:{port}"
    
    @property
    def SERVER_HOST(self):
        """Server host for external access (for image URLs)"""
        return self._get_cached_value('SERVER_HOST', 'localhost')
    
    @property
    def DEBUG(self):
        """FastAPI debug mode setting"""
        return self._get_cached_value('DEBUG', 'False').lower() == 'true'
    
    @property
    def LOG_LEVEL(self):
        """Logging level"""
        level = self._get_cached_value('LOG_LEVEL', 'INFO').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            logger.warning(f"Invalid LOG_LEVEL '{level}', using INFO")
            return 'INFO'
        return level
    
    # ============================================================================
    # IMAGE GENERATION DEFAULTS
    # ============================================================================
    
    @property
    def DEFAULT_IMAGE_SIZE(self):
        """Default image size"""
        return self._get_cached_value('DEFAULT_IMAGE_SIZE', '1328*1328')
    
    @property
    def DEFAULT_WATERMARK(self):
        """Default watermark setting"""
        return self._get_cached_value('DEFAULT_WATERMARK', 'false').lower() == 'true'
    
    @property
    def DEFAULT_PROMPT_EXTEND(self):
        """Default prompt extend setting"""
        return self._get_cached_value('DEFAULT_PROMPT_EXTEND', 'true').lower() == 'true'
    
    @property
    def ENABLE_PROMPT_ENHANCEMENT(self):
        """Enable prompt enhancement with LLM"""
        return self._get_cached_value('ENABLE_PROMPT_ENHANCEMENT', 'true').lower() == 'true'
    
    # ============================================================================
    # STORAGE CONFIGURATION
    # ============================================================================
    
    @property
    def TEMP_FOLDER(self):
        """Temporary folder for generated images"""
        return self._get_cached_value('TEMP_FOLDER', 'temp_images')
    
    # ============================================================================
    # API TIMEOUT SETTINGS
    # ============================================================================
    
    @property
    def API_TIMEOUT(self):
        """API request timeout in seconds"""
        try:
            val = int(self._get_cached_value('API_TIMEOUT', '60'))
            if val < 5 or val > 300:
                logger.warning(f"API_TIMEOUT {val} out of range, using 60")
                return 60
            return val
        except (ValueError, TypeError):
            logger.warning("Invalid API_TIMEOUT value, using 60")
            return 60
    
    @property
    def IMAGE_DOWNLOAD_TIMEOUT(self):
        """Image download timeout in seconds"""
        try:
            val = int(self._get_cached_value('IMAGE_DOWNLOAD_TIMEOUT', '30'))
            if val < 5 or val > 120:
                logger.warning(f"IMAGE_DOWNLOAD_TIMEOUT {val} out of range, using 30")
                return 30
            return val
        except (ValueError, TypeError):
            logger.warning("Invalid IMAGE_DOWNLOAD_TIMEOUT value, using 30")
            return 30
    
    # ============================================================================
    # PROMPT VALIDATION
    # ============================================================================
    
    @property
    def MIN_PROMPT_LENGTH(self):
        """Minimum prompt length"""
        try:
            return int(self._get_cached_value('MIN_PROMPT_LENGTH', '3'))
        except (ValueError, TypeError):
            return 3
    
    @property
    def MAX_PROMPT_LENGTH(self):
        """Maximum prompt length"""
        try:
            return int(self._get_cached_value('MAX_PROMPT_LENGTH', '1000'))
        except (ValueError, TypeError):
            return 1000
    
    # ============================================================================
    # CONFIGURATION VALIDATION
    # ============================================================================
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.DASHSCOPE_API_KEY:
            logger.error("DASHSCOPE_API_KEY not configured")
            return False
        return True
    
    def print_config_summary(self):
        """Print configuration summary"""
        logger.info("Configuration Summary:")
        logger.info(f"   FastAPI: {self.HOST}:{self.PORT} (Debug: {self.DEBUG})")
        logger.info(f"   DashScope Base URL: {self.DASHSCOPE_BASE_URL}")
        logger.info(f"   Image Model: {self.IMAGE_MODEL}")
        logger.info(f"   Video Model: {self.VIDEO_MODEL}")
        logger.info(f"   Text Model: {self.QWEN_TEXT_MODEL}")
        logger.info(f"   Default Image Size: {self.DEFAULT_IMAGE_SIZE}")
        logger.info(f"   Prompt Enhancement: {self.ENABLE_PROMPT_ENHANCEMENT}")


# Create global configuration instance
config = Config()

