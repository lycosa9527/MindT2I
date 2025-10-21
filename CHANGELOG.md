# Changelog

All notable changes to MindT2I will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.1] - 2025-10-22

### Fixed
- **Output Format Consistency**: All endpoints now return consistent plain text format
  - `/generate-image-text`: Returns markdown format `![]({image_url})` (matches MindGraph)
  - `/generate-video`: Returns user-friendly message "Please copy the link to your web browser to download the video, video URL: {url}"
  - `/generate` (intelligent): Now returns plain text instead of JSON
    - For images: Returns `![]({image_url})`
    - For videos: Returns download message
  - Error responses also return plain text for consistency
  - Better integration with DingTalk and other chat platforms

### Changed
- **Enhanced Logging**: Added comprehensive logging for prompt enhancement workflow
  - Qwen Turbo enhancement shows original and enhanced prompts
  - Image generation logs show final prompt sent to API
  - Video generation logs include all parameters and API-level enhancements
  - Full traceability from user input to final output

### Documentation
- **API Reference**: Created comprehensive `docs/API_REFERENCE.md` (875 lines)
  - Complete API documentation with examples
  - DashScope integration patterns
  - Request/response formats
  - Error handling guide
  - Best practices

- **Code Review**: Created detailed `docs/CODE_REVIEW.md` (1047 lines)
  - 40+ improvement recommendations
  - Priority-based implementation roadmap
  - Performance optimization opportunities
  - Testing strategy
  - Architecture enhancements

## [2.2.0] - 2025-10-22

### Added
- **Version Management**: Created `VERSION` file as single source of truth
  - Version now read from VERSION file instead of hardcoded
  - Easier version management across releases

### Changed
- **Image Generation Model**: Upgraded to `wan2.5-t2i-preview` via ImageSynthesis API
  - Previously used `qwen-image-plus` via MultiModal API
  - Better image quality and enhanced capabilities
  - Async task-based generation (consistent with video generation)
  - Expanded resolution options: 1280×1280, 1280×960, 1280×720, 1200×800, 800×1200, etc.
  - This is a MINOR version bump due to significant model upgrade

- **Video Generation**: Confirmed use of `wan2.5-t2v-preview` model
  - Already using latest model
  - 5s or 10s duration support
  - Audio generation support

- **User Interface**: Professional appearance improvements
  - Removed all emojis from debug interface
  - Clean, modern, professional design
  - Better suited for educational and business contexts

### Fixed
- **Configuration Management**: Updated model references throughout codebase
  - `IMAGE_MODEL=wan2.5-t2i-preview` (new default)
  - `VIDEO_MODEL=wan2.5-t2v-preview` (confirmed)
  - `QWEN_TEXT_MODEL=qwen-turbo` (unchanged - for prompt enhancement)
  - Updated `env.example` with detailed model documentation
  - Updated README.md model references and version history

### Removed
- **Project Cleanup**: Eliminated duplicate documentation files
  - Consolidated all documentation in `docs/` folder
  - Consolidated all tests in `tests/` folder
  - Root folder now contains only essential project files
  - Removed: CONCURRENCY_GUIDE.md, KEYWORD_DETECTION.txt, MIGRATION_GUIDE.md, 
    QUICKSTART.md, REACT_AGENT.md, VIDEO_API_UPDATES.md (from root)
  - Cleaner project structure following best practices

## [2.1.0] - 2025-01-21

### Added - Video Generation & Multi-User Support

#### Video Generation System
- **Text-to-Video Support**: Integrated DashScope wan2.5-t2v-preview model
  - Auto-generate audio or use custom audio files
  - Configurable duration: 5s or 10s
  - Multiple resolutions: 480P (832×480), 720P (1280×720), 1080P (1920×1080)
  - Optional watermark ("AI生成")
  - Negative prompt support for content exclusion
  - Random seed for reproducibility
  
- **Async Task-Based Generation** (Production Pattern)
  - Uses `VideoSynthesis.async_call()` + `wait()` pattern
  - Returns task_id immediately (< 1 second)
  - Automatic status polling (PENDING → RUNNING → SUCCEEDED)
  - Non-blocking for concurrent users
  - 1-5 minute generation time

- **Video Storage & Dual URLs**
  - Automatic video download with streaming (8KB chunks)
  - Local storage in `temp_videos/` folder
  - DashScope URL (valid 24h, fast CDN access)
  - Local URL (permanent, server storage)
  - User can choose which URL to use

- **Dedicated Video Endpoint**: `POST /generate-video`
  - Returns plain text format for DingTalk: `[video-download link][url]`
  - No intelligent routing, always generates video
  - 5-minute timeout for downloads

#### Intent Detection & Routing
- **ReAct Agent**: Simple keyword-based intent detection
  - Explicit keyword detection (< 1ms, no LLM calls)
  - Video keywords: video, videos, animation, clip, movie, film, 视频, 影片, 动画
  - Image keywords: image, picture, photo, pic, illustration, 图片, 图像, 照片, 画, 图
  - Defaults to image if no keywords found
  - No motion detection (user must be explicit)
  - Returns confidence score and reasoning
  
- **Unified Generation Service**: `POST /generate`
  - Intelligent routing based on keyword detection
  - Returns JSON with both `text` and `markdown` fields
  - Includes intent analysis (detected type, confidence, reasoning)
  - Works with both images and videos

#### Concurrency & Multi-User Support
- **Semaphore-Based Resource Management**
  - Max 20 concurrent video generations (`VIDEO_GENERATION_SEMAPHORE`)
  - Max 10 concurrent downloads (`VIDEO_DOWNLOAD_SEMAPHORE`)
  - Excess requests queue gracefully (no crashing)
  - Active operation logging
  
- **Production-Ready Configuration**
  - Uvicorn connection limit: 1000 concurrent connections
  - Keep-alive timeout: 120 seconds
  - Async I/O for all operations
  - Memory-efficient streaming downloads
  - Protects against API rate limits

- **Load Testing Tools**
  - `test_concurrent.py` - Test with 3, 10, or 25 concurrent users
  - Demonstrates non-blocking behavior
  - Validates queuing mechanism

#### API & Response Models
- **Video Response Model** (`VideoGenerationResponse`)
  - Complete video metadata (duration, size, audio status, model)
  - Original and enhanced prompts
  - Timestamp and request tracking
  
- **Enhanced Unified Response**
  - `url`: DashScope OSS URL or local URL
  - `local_url`: Permanent server URL (videos only)
  - `text`: Plain text format for DingTalk
  - `markdown`: HTML format for web display
  - `intent_analysis`: Detection details

#### UI & Debug Interface
- **Debug Page Updates** (`/debug`)
  - HTML5 video player with controls
  - Auto-detects media type (image/video)
  - Shows intent analysis and confidence scores
  - Separate download buttons for images/videos
  - Displays reasoning for routing decisions
  - Example prompts for both images and videos

### Changed
- **DashScope SDK**: Updated to version 1.20.11
- **Video Client**: Migrated from synchronous to async task-based pattern
- **Configuration**: Added video model settings and semaphore limits
- **Error Handling**: Enhanced for video generation failures
- **Static Files**: Added `/temp_videos` mount point
- **Logging**: Added active operation counters

### Documentation
- **`VIDEO_API_UPDATES.md`**: Complete API migration guide for wan2.5-t2v-preview
- **`REACT_AGENT.md`**: Intent agent documentation with keyword lists
- **`KEYWORD_DETECTION.txt`**: Quick reference for detection keywords
- **`CONCURRENCY_GUIDE.md`**: Multi-user support and load testing guide
- **`API_COMPARISON.md`**: Sync vs Async API pattern comparison
- **`test_concurrent.py`**: Concurrent load testing script
- **`test_video.py`**: Video endpoint testing script
- **`.gitignore`**: Updated to ignore temp files

### Technical Details
- **API Pattern**: Async task-based (async_call → wait → download)
- **Concurrency Model**: Semaphore-limited async operations
- **Storage**: Dual URL system (DashScope + Local)
- **Download Method**: Streaming with 8KB chunks
- **Video Expiry**: DashScope URLs expire in 24 hours
- **Generation Time**: 1-5 minutes per video
- **Capacity**: 10-50 concurrent users (current), 100+ with optimizations

### Performance
- **Task Creation**: < 1 second
- **Intent Detection**: < 1 millisecond (keyword matching)
- **Video Generation**: 1-5 minutes (DashScope processing)
- **Video Download**: 10-60 seconds (depends on size and network)
- **Concurrent Capacity**: 20 simultaneous generations, 10 simultaneous downloads

### Project Structure
- **Organized Root Directory**: Clean root with only essential files
  - Moved test files to `tests/` directory (4 test scripts)
  - Moved documentation to `docs/` directory (7 documentation files)
  - Created `docs/README.md` for documentation index
  - Created `tests/README.md` for testing guide
  - Updated internal links in README.md

### Dependencies
- **DashScope SDK**: Updated from 1.20.11 to 1.24.7 (latest)
  - 4 MINOR version updates (1.20 → 1.24)
  - Latest bug fixes and security patches
  - Improved performance and stability
  - Enhanced API compatibility

### Configuration
- **Video Parameters**: Now configurable via environment variables
  - `VIDEO_DEFAULT_SIZE`: Default video resolution (default: 1920*1080)
  - `VIDEO_DEFAULT_DURATION`: Default video duration in seconds (default: 10)
  - `VIDEO_PROMPT_EXTEND`: Enable prompt enhancement (default: true)
  - `VIDEO_WATERMARK`: Add watermark to videos (default: false)
  - `VIDEO_AUDIO`: Enable auto-generated audio (default: true)
  - All parameters documented in `env.example` with examples
  - No more hardcoded values in source code
  - Easy customization for different use cases (quality/balanced/budget)

### Image Generation
- **Unified Architecture**: Migrated to ImageSynthesis API
  - Model: `wan2.5-t2i-preview` (latest, supports 2000 char prompts)
  - Fallback: `wan2.2-t2i-flash` (fast, 800 char prompts)
  - Pattern: Async task-based (same as video)
  - API: `ImageSynthesis.async_call()` + `wait()`
  - Response: Direct URL (no complex parsing)
  - Created `clients/image.py` with unified pattern
  - Legacy `multimodal_client` kept for backward compatibility
- **Image Parameters**: Now configurable via environment variables
  - `IMAGE_MODEL`: Image generation model (default: wan2.5-t2i-preview)
  - `IMAGE_DEFAULT_SIZE`: Default resolution (default: 1280*960, 4:3 aspect ratio)
  - `IMAGE_PROMPT_EXTEND`: Enable prompt enhancement (default: true for best quality)
  - `IMAGE_WATERMARK`: Add watermark to images (default: false)
  - Model-specific defaults (wan2.5: 1280*960, wan2.2: 1024*1024)
  - All parameters documented in `env.example`

### User Experience
- **ASCII Banner**: Added stylish startup banner
  - Professional MindT2I branding with ASCII art
  - Shows version, features, and capabilities
  - Displays server configuration and quick links
  - Lists all available API endpoints
  - Created `utils/banner.py` module

## [2.0.0] - 2025-01-18

### Changed - FastAPI Migration
- **Complete Rewrite**: Migrated from Flask to FastAPI
  - Modern async/await architecture
  - Automatic OpenAPI documentation
  - Type-safe Pydantic models
  - Better performance with async I/O

- **Modular Architecture**: Organized codebase
  - `config/` - Centralized configuration
  - `clients/` - API clients (multimodal, text, video)
  - `models/` - Request/response models
  - `routers/` - API endpoints
  - `services/` - Business logic
  - `agents/` - Intent detection

- **LLM Integration**: Copied from MindGraph
  - Text client for prompt enhancement
  - MultiModal client for image generation
  - Async HTTP client wrapper

### Added
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- Custom debug interface at `/debug`
- Health check endpoint at `/health`
- Request/response validation with Pydantic
- Automatic image cleanup service

### Removed
- Old Flask framework (`app.py`)
- Legacy test files
- `README_v2.md` (consolidated into README)
- Demo scripts

## [1.0.0] - Initial Release

### Features
- Text-to-image generation using Qwen Image Plus
- Prompt enhancement with Qwen Turbo
- Local image storage
- Basic web interface
- Flask-based API

---

**Migration Notes**: 
- v1.x users should refer to `MIGRATION_GUIDE.md` for FastAPI migration
- Video generation requires DashScope API access
- Video URLs are temporary (24-hour expiration)

**Breaking Changes**:
- v2.0.0: Complete API redesign (Flask → FastAPI)
- v2.1.0: `/generate` endpoint now returns video or image based on prompt

---

Made with ❤️ by MindSpring Team | Author: lycosa9527
