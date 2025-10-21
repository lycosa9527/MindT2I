"""
Response Models for MindT2I API
"""

from pydantic import BaseModel, Field
from typing import Optional


class ImageGenerationResponse(BaseModel):
    """Response model for successful image generation"""
    
    success: bool = Field(
        default=True,
        description="Whether the generation was successful"
    )
    
    image_url: str = Field(
        ...,
        description="URL of the generated image",
        example="http://localhost:9528/temp_images/generated_20250831_161449_abc123.jpg"
    )
    
    markdown_image: str = Field(
        ...,
        description="Markdown format for embedding the image",
        example="![](http://localhost:9528/temp_images/generated_20250831_161449_abc123.jpg)"
    )
    
    message: str = Field(
        default="Image generated successfully",
        description="Status message"
    )
    
    filename: str = Field(
        ...,
        description="Filename of the generated image",
        example="generated_20250831_161449_abc123.jpg"
    )
    
    size: str = Field(
        ...,
        description="Size of the generated image",
        example="1328*1328"
    )
    
    prompt_enhanced: bool = Field(
        ...,
        description="Whether the prompt was enhanced"
    )
    
    original_prompt: str = Field(
        ...,
        description="Original user prompt"
    )
    
    enhanced_prompt: Optional[str] = Field(
        default=None,
        description="Enhanced prompt (if enhancement was enabled)"
    )
    
    timestamp: str = Field(
        ...,
        description="Timestamp of generation",
        example="20250831_161449"
    )
    
    request_id: str = Field(
        ...,
        description="Unique request identifier",
        example="abc123de-f456-7890-ghij-klmnopqrstuv"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for successful video generation"""
    
    success: bool = Field(
        default=True,
        description="Whether the generation was successful"
    )
    
    video_url: str = Field(
        ...,
        description="URL of the generated video (valid for 24 hours)",
        example="https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/xxx.mp4"
    )
    
    message: str = Field(
        default="Video generated successfully",
        description="Status message"
    )
    
    size: str = Field(
        ...,
        description="Size of the generated video",
        example="1280*720"
    )
    
    duration: int = Field(
        ...,
        description="Duration of video in seconds",
        example=5
    )
    
    prompt_enhanced: bool = Field(
        ...,
        description="Whether the prompt was enhanced"
    )
    
    original_prompt: str = Field(
        ...,
        description="Original user prompt"
    )
    
    enhanced_prompt: Optional[str] = Field(
        default=None,
        description="Enhanced prompt (if enhancement was enabled)"
    )
    
    timestamp: str = Field(
        ...,
        description="Timestamp of generation",
        example="20250831_161449"
    )
    
    has_audio: bool = Field(
        default=False,
        description="Whether video has audio"
    )
    
    model: str = Field(
        ...,
        description="Model used for generation",
        example="wan2.5-t2v-preview"
    )


class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    success: bool = Field(
        default=False,
        description="Always false for error responses"
    )
    
    error: str = Field(
        ...,
        description="Error message",
        example="Invalid prompt: too short"
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="Error code for programmatic handling",
        example="INVALID_PROMPT"
    )
    
    details: Optional[str] = Field(
        default=None,
        description="Additional error details"
    )

