# MindT2I API Reference

Complete API reference for MindT2I v2.2.0 - AI-Powered Image & Video Generation

**Author**: lycosa9527  
**Made by**: MTEL Team from Educational Technology, Beijing Normal University

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Models & Clients](#models--clients)
5. [Request/Response Schemas](#requestresponse-schemas)
6. [Error Handling](#error-handling)
7. [DashScope Integration](#dashscope-integration)
8. [Rate Limits & Quotas](#rate-limits--quotas)

---

## Overview

MindT2I provides a unified API for generating images and videos from text prompts, with intelligent routing, K12 educational enhancement, and comprehensive safety features.

### Base URL
```
http://localhost:9528
```

### Key Features
- **Intelligent Routing**: Automatic detection of image vs video intent
- **K12 Enhancement**: Educational content optimization via Qwen Turbo
- **Dual Model Support**: wan2.5-t2i-preview (images) and wan2.5-t2v-preview (videos)
- **Async Architecture**: Full FastAPI async/await for high concurrency
- **Safety First**: Educational content filtering and appropriateness checks

---

## Authentication

MindT2I uses DashScope API keys for backend LLM access.

### Configuration
Set in `.env` file:
```env
DASHSCOPE_API_KEY=sk-your-api-key-here
```

### Client Applications
No authentication required for local development. For production:
- Add API key authentication in middleware
- Use JWT tokens for user sessions
- Implement rate limiting per user/IP

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "MindT2I",
  "version": "2.2.0"
}
```

---

### 2. System Status

Get detailed application metrics.

**Endpoint**: `GET /status`

**Response**:
```json
{
  "status": "running",
  "framework": "FastAPI",
  "version": "2.2.0",
  "uptime_seconds": 1234.5,
  "memory_percent": 45.2,
  "timestamp": 1729584000.0
}
```

---

### 3. Intelligent Generation (Recommended)

Automatically detects whether to generate image or video based on prompt.

**Endpoint**: `POST /generate`

**Request Body**:
```json
{
  "prompt": "一只小猫在月光下奔跑"
}
```

**Optional Parameters**:
```json
{
  "prompt": "string (required)",
  "size": "string (optional, uses .env default)",
  "watermark": "boolean (optional, uses .env default)",
  "negative_prompt": "string (optional)",
  "prompt_extend": "boolean (optional, uses .env default)"
}
```

**Response (Image)**:
```json
{
  "success": true,
  "type": "image",
  "url": "http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg",
  "image_url": "http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg",
  "markdown": "![](http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg)",
  "filename": "generated_20251022_123456_abc123.jpg",
  "size": "1280*1280",
  "prompt_enhanced": true,
  "original_prompt": "一只小猫在月光下奔跑",
  "enhanced_prompt": "A curious young cat running gracefully...",
  "timestamp": "20251022_123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "intent_analysis": {
    "detected_type": "image",
    "confidence": 0.8,
    "reasoning": "No explicit keywords found, defaulting to image",
    "original_prompt": "一只小猫在月光下奔跑",
    "enhanced_prompt": "A curious young cat running gracefully..."
  }
}
```

**Response (Video)**:
```json
{
  "success": true,
  "type": "video",
  "url": "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/video.mp4",
  "local_url": "http://localhost:9528/temp_videos/generated_20251022_123456_abc123.mp4",
  "filename": "generated_20251022_123456_abc123.mp4",
  "text": "Please copy the link to your web browser to download the video, video URL: https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/video.mp4",
  "message": "Please copy the link to your web browser to download the video, video URL: https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/video.mp4",
  "markdown": "<video src='http://localhost:9528/temp_videos/generated_20251022_123456_abc123.mp4' controls></video>",
  "size": "1920*1080",
  "duration": 10,
  "timestamp": "20251022_123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "has_audio": true,
  "model": "wan2.5-t2v-preview",
  "intent_analysis": {
    "detected_type": "video",
    "confidence": 1.0,
    "reasoning": "Explicit video keyword detected: 'video'",
    "original_prompt": "Generate a video of...",
    "enhanced_prompt": "..."
  }
}
```

**Note**: The `text` and `message` fields contain the same user-friendly download instruction.

---

**Intent Detection Keywords**:
- **Video**: video, videos, animation, clip, movie, film, 视频, 影片, 动画
- **Image**: image, picture, photo, pic, illustration, 图片, 图像, 照片, 画, 图
- **Default**: If no keywords found, defaults to image

---

### 4. Force Image Generation (JSON Format)

Generate an image without intent detection. Returns full JSON with metadata.

**Endpoint**: `POST /generate-image`

**Request Body**: Same as `/generate`

**Response** (JSON):
```json
{
  "success": true,
  "image_url": "http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg",
  "markdown_image": "![](http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg)",
  "message": "Image generated successfully",
  "filename": "generated_20251022_123456_abc123.jpg",
  "size": "1280*1280",
  "prompt_enhanced": true,
  "original_prompt": "生成学生在教室和猫玩的素材图片",
  "enhanced_prompt": "A group of diverse students...",
  "timestamp": "20251022_123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Note**: Returns full JSON object. For plain text output (DingTalk/chat integration), use `/generate-image-text` instead.

---

### 5. Force Image Generation (Plain Text - DingTalk Format)

Generate an image and return markdown format for DingTalk/chat integration.

**Endpoint**: `POST /generate-image-text`

**Request Body**: Same as `/generate`

**Response** (plain text, markdown format):
```
![](http://localhost:9528/temp_images/generated_20251022_123456_abc123.jpg)
```

**Note**: Returns plain text in markdown image format `![](url)`, matching MindGraph's `generate_dingtalk` format. Use this for DingTalk/chat bot integration, NOT `/generate-image` which returns JSON.

---

### 6. Force Video Generation

Generate a video without intent detection.

**Endpoint**: `POST /generate-video`

**Request Body**: Same as `/generate`

**Response** (plain text, user-friendly format):
```
Please copy the link to your web browser to download the video, video URL: https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/video.mp4
```

**Note**: This endpoint returns plain text, not JSON. For DingTalk/chat integration.

---

### 7. Debug Interface

Interactive web UI for testing.

**Endpoint**: `GET /debug`

**Response**: HTML page with interactive form

**Features**:
- Prompt input
- Auto-detect image/video
- Real-time generation
- Download/preview results
- History tracking

---

### 8. API Documentation

Auto-generated OpenAPI documentation.

**Endpoints**:
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

---

## Models & Clients

### Image Generation

**Model**: `wan2.5-t2i-preview`  
**API**: DashScope ImageSynthesis  
**Client**: `clients/image.py`

**Supported Sizes**:
- `1280*1280` - 1:1 square (default)
- `1280*960` - 4:3 landscape
- `960*1280` - 3:4 portrait
- `1280*720` - 16:9 landscape
- `720*1280` - 9:16 portrait
- `1200*800` - 3:2 landscape
- `800*1200` - 2:3 portrait
- `1344*576` - 21:9 ultra-wide

**Parameters**:
```python
{
  "prompt": str,              # Required
  "size": str,                # Optional, default from .env
  "n": int,                   # Number of images (default: 1)
  "prompt_extend": bool,      # API-level enhancement
  "watermark": bool,          # Add watermark
  "negative_prompt": str,     # Content to avoid
  "seed": int                 # Reproducibility
}
```

**Generation Time**: 10-20 seconds  
**Output**: URL valid for 24 hours

---

### Video Generation

**Model**: `wan2.5-t2v-preview`  
**API**: DashScope VideoSynthesis  
**Client**: `clients/video.py`

**Supported Sizes**:

720P (default):
- `1280*720` - 16:9 landscape
- `720*1280` - 9:16 portrait
- `960*960` - 1:1 square
- `1088*832` - 4:3 landscape
- `832*1088` - 3:4 portrait

1080P:
- `1920*1080` - 16:9 landscape
- `1080*1920` - 9:16 portrait
- `1440*1440` - 1:1 square
- `1632*1248` - 4:3 landscape
- `1248*1632` - 3:4 portrait

480P:
- `832*480` - 16:9 landscape
- `480*832` - 9:16 portrait
- `624*624` - 1:1 square

**Parameters**:
```python
{
  "prompt": str,              # Required
  "size": str,                # Optional, default from .env
  "duration": int,            # 5 or 10 seconds
  "prompt_extend": bool,      # API-level enhancement
  "watermark": bool,          # Add "AI生成" watermark
  "audio": bool,              # Auto-generate audio
  "audio_url": str,           # Custom audio file URL
  "negative_prompt": str,     # Content to avoid
  "seed": int                 # Reproducibility
}
```

**Generation Time**: 1-5 minutes  
**Output**: URL valid for 24 hours  
**Concurrency**: Max 20 concurrent generations (semaphore-controlled)

---

### Prompt Enhancement

**Model**: `qwen-turbo`  
**API**: DashScope Text Generation  
**Client**: `clients/multimodal.py`

**Purpose**: Enhance user prompts with K12 educational context

**Enhancement Process**:
1. User submits simple prompt
2. Qwen Turbo adds educational context, safety checks, learning objectives
3. Enhanced prompt sent to image/video API
4. wan2.5 may do additional internal enhancement

**Parameters**:
```python
{
  "max_tokens": 300,          # Max response length
  "temperature": 0.7,         # Creativity (0.0-1.0)
  "top_p": 0.8               # Diversity
}
```

**Enable/Disable**: Set `ENABLE_PROMPT_ENHANCEMENT` in `.env`

---

## Request/Response Schemas

### ImageGenerationRequest

```python
{
  "prompt": str,                    # Required, 3-1000 chars
  "size": str = "1328*1328",        # Optional
  "watermark": bool = False,        # Optional
  "negative_prompt": str = "",      # Optional
  "prompt_extend": bool = True      # Optional
}
```

### ImageGenerationResponse

```python
{
  "success": bool,
  "image_url": str,                 # Full server URL
  "markdown_image": str,            # Markdown syntax
  "message": str,
  "filename": str,
  "size": str,
  "prompt_enhanced": bool,
  "original_prompt": str,
  "enhanced_prompt": str | None,
  "timestamp": str,
  "request_id": str                 # UUID
}
```

### ErrorResponse

```python
{
  "success": false,
  "error": str,                     # Error message
  "error_code": str,                # Error code
  "details": str | None             # Optional details
}
```

**Error Codes**:
- `VALIDATION_ERROR` - Invalid request parameters
- `GENERATION_FAILED` - API call failed
- `DOWNLOAD_FAILED` - Failed to download result
- `TIMEOUT` - Request timeout
- `API_ERROR` - DashScope API error

---

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (validation error)
- `422` - Unprocessable Entity (Pydantic validation)
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Response Format

```json
{
  "detail": {
    "success": false,
    "error": "Failed to generate image",
    "error_code": "GENERATION_FAILED",
    "details": "API returned status 429: Rate limit exceeded"
  }
}
```

### Common Errors

**1. Prompt Too Short**
```json
{
  "detail": {
    "success": false,
    "error": "Prompt is too short (min 3 characters)",
    "error_code": "VALIDATION_ERROR"
  }
}
```

**2. API Key Invalid**
```json
{
  "detail": {
    "success": false,
    "error": "Failed to generate image",
    "error_code": "GENERATION_FAILED",
    "details": "DashScope API error: 401 - Invalid API key"
  }
}
```

**3. Rate Limit**
```json
{
  "detail": {
    "success": false,
    "error": "Failed to generate image",
    "error_code": "GENERATION_FAILED",
    "details": "DashScope API error: 429 - Rate limit exceeded"
  }
}
```

---

## DashScope Integration

### Async Task Pattern

MindT2I uses DashScope's async task pattern for both image and video generation.

#### Image Generation Flow

```python
# Step 1: Create async task
task_response = ImageSynthesis.async_call(
    api_key=api_key,
    model="wan2.5-t2i-preview",
    prompt=prompt,
    size="1280*1280"
)

# Returns immediately with task_id
task_id = task_response.output.task_id  # < 1 second

# Step 2: Wait for completion (polls automatically)
final_response = ImageSynthesis.wait(task_response)

# Returns when done (10-20 seconds)
image_url = final_response.output.results[0].url
```

#### Video Generation Flow

```python
# Step 1: Create async task
task_response = VideoSynthesis.async_call(
    api_key=api_key,
    model="wan2.5-t2v-preview",
    prompt=prompt,
    size="1920*1080",
    duration=10
)

# Returns immediately with task_id
task_id = task_response.output.task_id  # < 1 second

# Step 2: Wait for completion (polls every 15s)
final_response = VideoSynthesis.wait(task_response)

# Returns when done (1-5 minutes)
video_url = final_response.output.video_url
```

#### Task Status Flow

```
PENDING → RUNNING → SUCCEEDED
                 ↘ FAILED
                 ↘ CANCELED
```

#### Status Checking (Optional)

```python
# Check task status manually
status = ImageSynthesis.fetch(task_response)
print(status.output.task_status)  # PENDING, RUNNING, SUCCEEDED, FAILED
```

### Prompt Enhancement Fields

DashScope returns enhanced prompts:

```python
{
  "output": {
    "results": [{
      "url": "...",
      "orig_prompt": "Original user prompt",
      "actual_prompt": "Enhanced prompt by model"
    }]
  }
}
```

---

## Rate Limits & Quotas

### DashScope Limits

Varies by account tier. Check your DashScope console for:
- Requests per minute (RPM)
- Requests per day (RPD)
- Concurrent tasks

### MindT2I Internal Limits

**Video Generation**:
- Max 20 concurrent generations (semaphore)
- Max 10 concurrent downloads (semaphore)

**Configuration**:
```python
# services/unified_service.py
VIDEO_GENERATION_SEMAPHORE = asyncio.Semaphore(20)
VIDEO_DOWNLOAD_SEMAPHORE = asyncio.Semaphore(10)
```

### Timeout Settings

Configured in `.env`:
```env
API_TIMEOUT=60                    # General API timeout
IMAGE_DOWNLOAD_TIMEOUT=30         # Image download timeout
# Video download: 300s (hardcoded)
```

---

## Configuration Reference

### Environment Variables

See `env.example` for complete list. Key settings:

```env
# API
DASHSCOPE_API_KEY=sk-xxx

# Models
IMAGE_MODEL=wan2.5-t2i-preview
VIDEO_MODEL=wan2.5-t2v-preview
QWEN_TEXT_MODEL=qwen-turbo

# Defaults
DEFAULT_IMAGE_SIZE=1328*1328
DEFAULT_WATERMARK=false
DEFAULT_PROMPT_EXTEND=true
ENABLE_PROMPT_ENHANCEMENT=true

# Image Settings
IMAGE_DEFAULT_SIZE=1280*960
IMAGE_PROMPT_EXTEND=true
IMAGE_WATERMARK=false

# Video Settings
VIDEO_DEFAULT_SIZE=1920*1080
VIDEO_DEFAULT_DURATION=10
VIDEO_PROMPT_EXTEND=true
VIDEO_WATERMARK=false
VIDEO_AUDIO=true
```

---

## Code Examples

### Python (Async)

```python
import aiohttp
import asyncio

async def generate_image(prompt: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:9528/generate",
            json={"prompt": prompt}
        ) as response:
            result = await response.json()
            if result["type"] == "image":
                print(f"Image URL: {result['url']}")
            else:
                print(f"Video URL: {result['url']}")

asyncio.run(generate_image("A cat in a classroom"))
```

### Python (Sync)

```python
import requests

response = requests.post(
    "http://localhost:9528/generate-image",
    json={"prompt": "A cat in a classroom"}
)

result = response.json()
print(f"Image URL: {result['image_url']}")
```

### cURL

```bash
# Intelligent generation
curl -X POST http://localhost:9528/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "一只小猫在教室里玩耍"}'

# Force image
curl -X POST http://localhost:9528/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A sunset over mountains"}'

# Plain text response
curl -X POST http://localhost:9528/generate-image-text \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful landscape"}'
```

### JavaScript/TypeScript

```typescript
async function generateContent(prompt: string) {
  const response = await fetch('http://localhost:9528/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  
  const result = await response.json();
  
  if (result.type === 'image') {
    console.log('Image URL:', result.url);
    document.getElementById('output').innerHTML = 
      `<img src="${result.url}" alt="Generated image">`;
  } else {
    console.log('Video URL:', result.url);
    document.getElementById('output').innerHTML = 
      `<video src="${result.local_url}" controls></video>`;
  }
}
```

---

## Best Practices

### 1. Use Intelligent Generation

Use `/generate` endpoint for automatic routing:
```python
# Good: Auto-detects
POST /generate {"prompt": "Generate a video of..."}

# Less ideal: Manual routing
POST /generate-video {"prompt": "A video of..."}
```

### 2. Enable Prompt Enhancement

For K12 use, keep `ENABLE_PROMPT_ENHANCEMENT=true`:
- Adds educational context
- Ensures safety and appropriateness
- Improves image quality

### 3. Handle Async Responses

Expect 10-30s for images, 1-5min for videos:
```javascript
// Show loading indicator
showLoading();

const response = await fetch('/generate', {
  method: 'POST',
  body: JSON.stringify({prompt})
});

hideLoading();
```

### 4. Error Handling

Always handle errors gracefully:
```python
try:
    response = await generate_image(prompt)
except HTTPException as e:
    if e.status_code == 400:
        # Validation error
        print("Invalid request:", e.detail)
    elif e.status_code == 500:
        # Server error
        print("Generation failed:", e.detail)
```

### 5. Resource Cleanup

Old images are auto-cleaned after 24h. For custom cleanup:
```python
from services.image_service import image_service

# Clean images older than 12 hours
image_service.cleanup_old_images(max_age_hours=12)
```

---

## Performance Optimization

### 1. Concurrent Requests

FastAPI handles multiple concurrent requests:
```python
# Multiple users can generate simultaneously
await asyncio.gather(
    generate_image("prompt1"),
    generate_image("prompt2"),
    generate_image("prompt3")
)
```

### 2. Caching

Consider caching enhanced prompts:
```python
# Cache Qwen Turbo enhancements for common prompts
cache = {}
if prompt in cache:
    enhanced = cache[prompt]
else:
    enhanced = await text_client.enhance_prompt(prompt)
    cache[prompt] = enhanced
```

### 3. Disable Enhancement for Speed

For faster generation (without K12 context):
```env
ENABLE_PROMPT_ENHANCEMENT=false
```

This saves ~2 seconds per request.

---

## Troubleshooting

### Logs

Check `logs/app.log` for detailed information:
```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# View prompt enhancement
grep "PROMPT ENHANCEMENT" logs/app.log
```

### Common Issues

**1. Prompt Enhancement Not Working**
- Check `ENABLE_PROMPT_ENHANCEMENT=true` in `.env`
- Verify `DASHSCOPE_API_KEY` is valid
- Check logs for Qwen Turbo errors

**2. Slow Generation**
- Images: 10-20s is normal
- Videos: 1-5min is normal
- If slower: Check DashScope service status

**3. Video Concurrency Errors**
- Max 20 concurrent video generations
- Requests queue automatically
- Monitor semaphore usage in logs

---

## Version History

**v2.2.0** (Current - 2025-10-22)
- Updated to wan2.5-t2i-preview and wan2.5-t2v-preview
- Enhanced logging system
- VERSION file for version management
- Simplified debug UI

**v2.1.0** (2025-01-21)
- Added video generation support
- ReAct agent for intelligent routing
- Concurrency controls

**v2.0.0** (2025-01-18)
- Complete FastAPI rewrite
- Async/await architecture
- Modular codebase

---

## Support & Resources

- **Documentation**: `/docs` (Swagger UI)
- **Source Code**: See project structure
- **Logs**: `logs/app.log`
- **Configuration**: `env.example`
- **DashScope Docs**: https://help.aliyun.com/zh/model-studio/

---

**Made with ❤️ by MindSpring Team | Author: lycosa9527**

