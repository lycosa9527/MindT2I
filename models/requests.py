"""
Request Models for MindT2I API
"""

from pydantic import BaseModel, Field
from typing import Optional


class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    
    prompt: str = Field(
        ...,
        description="Text description for image generation",
        min_length=3,
        max_length=1000,
        example="一副典雅庄重的对联悬挂于厅堂之中"
    )
    
    size: Optional[str] = Field(
        default="1328*1328",
        description="Image size (format: width*height)",
        example="1328*1328"
    )
    
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to add watermark to the image"
    )
    
    negative_prompt: Optional[str] = Field(
        default="",
        description="Negative prompt to avoid certain elements",
        example="dark, gloomy"
    )
    
    prompt_extend: Optional[bool] = Field(
        default=True,
        description="Whether to extend/enhance the prompt automatically"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置",
                "size": "1328*1328",
                "watermark": False,
                "negative_prompt": "",
                "prompt_extend": True
            }
        }

