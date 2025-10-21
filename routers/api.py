"""
API Router for MindT2I
======================

Handles image generation API endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from models.requests import ImageGenerationRequest
from models.responses import ImageGenerationResponse, ErrorResponse
from services.image_service import image_service
from services.unified_service import unified_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")


@router.post(
    "/generate-image",
    response_model=ImageGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Image Generation"],
    summary="Generate image from text prompt",
    description="Generate an image using Qwen Image Plus via DashScope MultiModal API"
)
async def generate_image(request: ImageGenerationRequest):
    """
    Generate image from text prompt
    
    - **prompt**: Text description for image generation (required)
    - **size**: Image size, e.g., "1328*1328" (optional, default: "1328*1328")
    - **watermark**: Add watermark to image (optional, default: false)
    - **negative_prompt**: Negative prompt to avoid certain elements (optional)
    - **prompt_extend**: Auto-extend/enhance prompt (optional, default: true)
    
    Returns the generated image URL and metadata.
    """
    try:
        logger.info(f"Image generation request - Prompt: {request.prompt[:50]}...")
        
        result = await image_service.generate_image(
            prompt=request.prompt,
            size=request.size,
            watermark=request.watermark,
            negative_prompt=request.negative_prompt,
            prompt_extend=request.prompt_extend
        )
        
        logger.info("=" * 80)
        logger.info("/generate-image ENDPOINT - RESPONSE")
        logger.info("=" * 80)
        logger.info(f"Result from image_service:")
        logger.info(f"  image_url: {result.get('image_url')}")
        logger.info(f"  markdown_image: {result.get('markdown_image')}")
        logger.info(f"  filename: {result.get('filename')}")
        logger.info("=" * 80)
        
        return ImageGenerationResponse(**result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to generate image",
                "error_code": "GENERATION_FAILED",
                "details": str(e)
            }
        )


@router.post(
    "/generate-image-text",
    response_class=PlainTextResponse,
    tags=["Image Generation"],
    summary="Generate image and return markdown format",
    description="Generate an image and return markdown image syntax as plain text"
)
async def generate_image_text(request: ImageGenerationRequest):
    """
    Generate image and return markdown syntax for easy embedding
    
    This endpoint returns the markdown image syntax as plain text,
    which is useful for direct embedding in markdown editors or chat applications.
    
    - **prompt**: Text description for image generation (required)
    - **size**: Image size, e.g., "1328*1328" (optional, default: "1328*1328")
    - **watermark**: Add watermark to image (optional, default: false)
    - **negative_prompt**: Negative prompt to avoid certain elements (optional)
    - **prompt_extend**: Auto-extend/enhance prompt (optional, default: true)
    
    Returns markdown format: ![](http://server:port/temp_images/filename.jpg)
    """
    try:
        logger.info(f"Plain text image generation request - Prompt: {request.prompt[:50]}...")
        
        result = await image_service.generate_image(
            prompt=request.prompt,
            size=request.size,
            watermark=request.watermark,
            negative_prompt=request.negative_prompt,
            prompt_extend=request.prompt_extend
        )
        
        logger.info("=" * 80)
        logger.info("/generate-image-text ENDPOINT - PLAIN TEXT RESPONSE")
        logger.info("=" * 80)
        logger.info(f"Result from image_service:")
        logger.info(f"  image_url: {result.get('image_url')}")
        logger.info(f"  markdown_image: {result.get('markdown_image')}")
        
        # Return markdown format for easy embedding
        markdown = result['markdown_image']
        logger.info(f"Returning plain text: {markdown}")
        logger.info("=" * 80)
        
        return PlainTextResponse(content=markdown)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return PlainTextResponse(
            content=f"Error: {str(e)}",
            status_code=400
        )
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        return PlainTextResponse(
            content=f"Error: Failed to generate image - {str(e)}",
            status_code=500
        )


@router.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Health check endpoint"""
    from config.settings import config
    return {
        "status": "healthy",
        "service": "MindT2I",
        "version": config.VERSION
    }


@router.get(
    "/debug",
    response_class=HTMLResponse,
    tags=["Development"],
    summary="Debug interface",
    description="Interactive web interface for testing image generation"
)
async def debug_page(request: Request):
    """Serve the debug/testing interface"""
    return templates.TemplateResponse("debug.html", {"request": request})


@router.post(
    "/generate-video",
    tags=["Video Generation"],
    summary="Generate video from text prompt (plain text output)",
    description="Generate a video using DashScope VideoSynthesis API with user-friendly download message"
)
async def generate_video_text(request: ImageGenerationRequest):
    """
    Generate video from text prompt with plain text output.
    
    - **prompt**: Text description for video generation (required)
    - **size**: Video size (optional, auto-mapped from image size)
    
    Returns: "Please copy the link to your web browser to download the video, video URL: [url]"
    """
    try:
        logger.info(f"Video generation request - Prompt: {request.prompt[:50]}...")
        
        # Generate video using unified service (force video type)
        result = await unified_service.generate(
            prompt=request.prompt,
            size=request.size,
            watermark=request.watermark,
            negative_prompt=request.negative_prompt,
            prompt_extend=request.prompt_extend,
            force_type="video"  # Force video generation
        )
        
        logger.info("=" * 80)
        logger.info("VIDEO GENERATION COMPLETE - CONSTRUCTING RESPONSE")
        logger.info("=" * 80)
        logger.info(f"Result dict keys: {list(result.keys())}")
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Full result dict: {result}")
        
        # Return user-friendly message with download link
        video_url = result.get('url')
        plain_text = f"Please copy the link to your web browser to download the video, video URL: {video_url}"
        
        logger.info("-" * 80)
        logger.info("SENDING RESPONSE TO CLIENT")
        logger.info("-" * 80)
        logger.info(f"Response type: PlainTextResponse")
        logger.info(f"Status code: 200")
        logger.info(f"Content: {plain_text}")
        logger.info(f"Content length: {len(plain_text)} chars")
        logger.info("-" * 80)
        
        response = PlainTextResponse(
            content=plain_text,
            status_code=200
        )
        logger.info("Response object created successfully")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response media_type: {response.media_type}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return PlainTextResponse(
            content=f"Error: Invalid request - {str(e)}",
            status_code=400
        )
    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        return PlainTextResponse(
            content=f"Error: Failed to generate video - {str(e)}",
            status_code=500
        )


@router.post(
    "/generate",
    tags=["Intelligent Generation"],
    summary="Intelligent image/video generation (JSON output for web interface)",
    description="Uses ReAct agent to automatically determine if user wants image or video, then generates accordingly. Returns JSON with full metadata for web interface."
)
async def generate_intelligent(request: ImageGenerationRequest):
    """
    Intelligent generation endpoint with ReAct agent (JSON response).
    
    The agent analyzes your prompt using Qwen-turbo and automatically decides
    whether to generate an image or video based on motion indicators.
    
    Returns JSON with:
    - type: 'image' or 'video'
    - url: Direct URL to generated content
    - markdown: Formatted markdown for display
    - Full metadata (size, duration, intent_analysis, etc.)
    
    For plain text output (DingTalk/Chat), use:
    - `/generate-image-text` for images
    - `/generate-video` for videos
    
    Examples:
    - "一只小猫在月光下奔跑" → VIDEO (motion: running)
    - "A beautiful sunset over mountains" → IMAGE (static scene)
    - "狗狗在公园里玩耍" → VIDEO (motion: playing)
    """
    try:
        logger.info(f"Intelligent generation request - Prompt: {request.prompt[:50]}...")
        
        result = await unified_service.generate(
            prompt=request.prompt,
            size=request.size,
            watermark=request.watermark,
            negative_prompt=request.negative_prompt,
            prompt_extend=request.prompt_extend,
            force_type="auto"  # Use intelligent detection
        )
        
        # Return full JSON for web interface
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        logger.error(f"Intelligent generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to generate content",
                "error_code": "GENERATION_FAILED",
                "details": str(e)
            }
        )

