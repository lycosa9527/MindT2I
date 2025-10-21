# MindT2I - AI-Powered Text-to-Image Generation API

🎨 Modern async web application for AI-powered text-to-image generation using FastAPI and DashScope MultiModal API

**Made by MindSpring Team | Author: lycosa9527**

## 🚀 Features

### Core Functionality
- 🎨 **Text-to-Image Generation**: Convert text prompts into high-quality images using wan2.5-t2i-preview
- 🎬 **Text-to-Video Generation**: Create videos from text using wan2.5-t2v-preview
- 🧠 **ReAct Agent**: Intelligent agent that automatically detects if you want image or video
- 💡 **Smart Routing**: Analyzes prompts for motion keywords and routes to appropriate API
- 🚀 **AI-Powered Enhancement**: Automatically enhance prompts with Qwen Turbo
- 🌐 **RESTful API**: Clean, modern FastAPI endpoints with automatic OpenAPI documentation
- 💾 **Local Storage**: Generated images saved locally with automatic cleanup
- ⚡ **High Performance**: Full async/await support for concurrent requests
- 📱 **Auto Documentation**: Interactive API docs at `/docs` and `/redoc`

### Enterprise Features
- 🔒 **Type Safety**: Pydantic models for request/response validation
- 🏥 **Health Monitoring**: Comprehensive system health checks and metrics
- 🧹 **Automatic Cleanup**: Configurable cleanup of old temporary images
- 🌍 **Cross-Platform**: Works on Windows, Linux, and macOS
- 📊 **Professional Logging**: Structured, colored logging with multiple levels
- ⚙️ **Configuration Management**: Environment-based configuration with validation
- 🚨 **Error Handling**: Structured error responses with proper HTTP status codes

## 📋 Quick Start

### Prerequisites
- Python 3.8 or higher
- DashScope API key from Alibaba Cloud
- Internet connection for API calls

### Installation

   ```bash
# 1. Navigate to project directory
cd "C:\Users\roywa\Documents\Cursor Projects\MindT2I"

# 2. Install dependencies
   pip install -r requirements.txt

# 3. Configure environment
copy env.example .env  # Windows
# cp env.example .env  # Linux/Mac

# Edit .env and set your API key
# DASHSCOPE_API_KEY=your_api_key_here

# 4. Run the server
python main.py
   ```

The application will start on `http://localhost:9528`

## 📁 Project Structure

```
MindT2I/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Centralized config with env variables
├── clients/               # LLM clients
│   ├── __init__.py
│   └── multimodal.py     # DashScope MultiModal & Text clients
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── requests.py       # Request models
│   └── responses.py      # Response models
├── routers/               # API routes
│   ├── __init__.py
│   └── api.py            # Image generation endpoints
├── services/              # Business logic
│   ├── __init__.py
│   └── image_service.py  # Image generation service
├── temp_images/           # Generated images (auto-created)
├── logs/                  # Application logs (auto-created)
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── test_fastapi.py      # Test suite
├── QUICKSTART.md        # Quick start guide
├── MIGRATION_GUIDE.md   # Migration guide
└── README.md            # This file
```

## 📡 API Endpoints

### 1. Generate Image (JSON Response)

**POST** `/generate-image`

Generate an image and return detailed JSON response.

**Request:**
```json
{
  "prompt": "一副典雅庄重的对联悬挂于厅堂之中",
  "size": "1328*1328",
  "watermark": false,
  "negative_prompt": "",
  "prompt_extend": true
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "http://localhost:9528/temp_images/generated_20250831_161449_abc123.jpg",
  "markdown_image": "![](http://localhost:9528/temp_images/generated_20250831_161449_abc123.jpg)",
  "message": "Image generated successfully",
  "filename": "generated_20250831_161449_abc123.jpg",
    "size": "1328*1328",
  "prompt_enhanced": true,
  "original_prompt": "一副典雅庄重的对联",
  "enhanced_prompt": "An elegant and dignified Chinese couplet...",
  "timestamp": "20250831_161449",
  "request_id": "abc123de-f456-7890-ghij-klmnopqrstuv"
}
```

### 2. Generate Image (Plain Text Response)

**POST** `/generate-image-text`

Generate an image and return only the plain text URL.

**Request:**
```json
{
  "prompt": "一只可爱的小猫在阳光明媚的花园里玩耍"
}
```

**Response (plain text):**
```
http://localhost:9528/temp_images/generated_20250831_161449_abc123.jpg
```

### 3. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
    "status": "healthy",
  "service": "MindT2I",
  "version": "2.0.0"
}
```

### 4. Status Check

**GET** `/status`

Get detailed application metrics.

**Response:**
```json
{
  "status": "running",
  "framework": "FastAPI",
  "version": "2.0.0",
  "uptime_seconds": 123.4,
  "memory_percent": 45.2,
  "timestamp": 1640995200.0
}
```

### 5. Debug Interface

**GET** `/debug`

Interactive web interface for testing image generation with:
- Beautiful modern UI
- Real-time image preview
- Image download and sharing
- Recent prompts history
- Example prompts
- Size and watermark controls

**Access at**: http://localhost:9528/debug

### 6. API Documentation

- **Swagger UI**: http://localhost:9528/docs
- **ReDoc**: http://localhost:9528/redoc

### 7. Intelligent Generation (NEW! 🧠)

**POST** `/generate`

**ReAct Agent** automatically detects if you want image or video!

```bash
curl -X POST "http://localhost:9528/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "一只小猫在月光下奔跑"}'
```

The agent will:
1. Check for explicit keywords ("video", "image", "picture", etc.)
2. Default to IMAGE if no keywords found
3. Route and generate IMMEDIATELY (< 1ms routing time!)

**Response includes reasoning:**
```json
{
  "type": "video",
  "url": "https://...",
  "intent_analysis": {
    "detected_type": "video",
    "confidence": 0.95,
    "reasoning": "Contains '奔跑' (running) which indicates motion"
  }
}
```

See [REACT_AGENT.md](docs/REACT_AGENT.md) for full documentation.

### 8. Access the Debug Interface

Open your browser and visit:
```
http://localhost:9528/debug
```

This gives you a beautiful interactive interface for testing!

### Request Parameters

**Required:**
- `prompt` (string): Text description for image generation

**Optional:**
- `size` (string): Image dimensions. Options:
  - `1664*928` (16:9 landscape)
  - `1472*1140` (4:3 landscape)
  - `1328*1328` (1:1 square) - **default**
  - `1140*1472` (3:4 portrait)
  - `928*1664` (9:16 portrait)
- `watermark` (boolean): Add watermark (default: `false`)
- `negative_prompt` (string): What to avoid in the image (default: `""`)
- `prompt_extend` (boolean): Auto-extend prompt (default: `true`)

## 💻 Usage Examples

### Python (Synchronous)

```python
import requests

response = requests.post(
    "http://localhost:9528/generate-image",
    json={"prompt": "A beautiful sunset over mountains"}
)

    result = response.json()
print(f"Image URL: {result['image_url']}")
```

### Python (Async)

```python
import aiohttp
import asyncio

async def generate_image():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:9528/generate-image",
            json={"prompt": "A beautiful sunset over mountains"}
        ) as response:
            result = await response.json()
            print(f"Image URL: {result['image_url']}")

asyncio.run(generate_image())
```

### cURL

```bash
curl -X POST "http://localhost:9528/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset over mountains"}'
```

### JavaScript

```javascript
const response = await fetch('http://localhost:9528/generate-image', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        prompt: "A beautiful sunset over mountains"
    })
});

const result = await response.json();
    console.log(`Image URL: ${result.image_url}`);
```

## ⚙️ Configuration

All configuration is managed through environment variables in `.env`:

### Required Settings
- `DASHSCOPE_API_KEY`: Your DashScope API key

### Server Settings
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `9528`)
- `SERVER_HOST`: Host for image URLs (default: `localhost`)
- `DEBUG`: Debug mode with auto-reload (default: `false`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Model Settings
- `IMAGE_MODEL`: Image generation model (default: `wan2.5-t2i-preview`)
- `VIDEO_MODEL`: Video generation model (default: `wan2.5-t2v-preview`)
- `QWEN_TEXT_MODEL`: Text model for enhancement (default: `qwen-turbo`)

### Image Generation Defaults
- `DEFAULT_IMAGE_SIZE`: Default size (default: `1328*1328`)
- `DEFAULT_WATERMARK`: Add watermark (default: `false`)
- `DEFAULT_PROMPT_EXTEND`: Auto-extend prompt (default: `true`)
- `ENABLE_PROMPT_ENHANCEMENT`: Use LLM enhancement (default: `true`)

### Advanced Settings
- `API_TIMEOUT`: API request timeout (default: `60` seconds)
- `IMAGE_DOWNLOAD_TIMEOUT`: Image download timeout (default: `30` seconds)
- `MIN_PROMPT_LENGTH`: Minimum prompt length (default: `3`)
- `MAX_PROMPT_LENGTH`: Maximum prompt length (default: `1000`)
- `TEMP_FOLDER`: Temporary images folder (default: `temp_images`)

See `env.example` for complete configuration template.

## 🧪 Testing

   ```bash
# Run the test suite
python tests/test_fastapi.py
```

The test suite includes:
- Health and status checks
- Image generation (JSON and plain text)
- Minimal request validation
- Error handling
- Timeout testing

## 🏗️ Architecture

### FastAPI Application
Modern async web framework with:
- Full async/await support for high performance
- Automatic OpenAPI documentation
- Pydantic models for type safety
- Built-in request validation

### LLM Client Layer
Clean abstraction for DashScope APIs:
- **MultiModalClient**: Image generation with Qwen Image Plus
- **TextClient**: Prompt enhancement with Qwen Turbo
- Async HTTP clients (aiohttp)
- Proper error handling and retries

### Service Layer
Business logic separation:
- Image generation workflow
- Prompt validation and enhancement
- File management and cleanup
- Error handling and logging

### Configuration Management
Centralized config with:
- Environment variable loading
- Property-based access with caching
- Validation and defaults
- Type safety

## 🔧 Development

### Running in Development Mode

```bash
# With auto-reload
python main.py  # Set DEBUG=true in .env

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 9528
```

### Production Deployment

```bash
# Set DEBUG=false in .env
uvicorn main:app --host 0.0.0.0 --port 9528 --workers 4
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :9528
taskkill /F /PID <PID>

# Linux/Mac
lsof -ti :9528 | xargs kill -9
```

### Module Not Found

```bash
# Make sure you're in the project root
cd "C:\Users\roywa\Documents\Cursor Projects\MindT2I"

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Issues

```bash
# Check your .env file
type .env  # Windows
cat .env   # Linux/Mac

# Make sure DASHSCOPE_API_KEY is set correctly
```

### Check Logs

```bash
# View application logs
type logs\app.log  # Windows
cat logs/app.log   # Linux/Mac
```

## 📚 Documentation

- **[API_REFERENCE.md](docs/API_REFERENCE.md)**: Complete API reference and integration guide
- **[QUICKSTART.md](docs/QUICKSTART.md)**: 5-minute quick start guide
- **[MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)**: Migration from Flask v1.0
- **[CHANGELOG.md](CHANGELOG.md)**: Detailed version history (v2.2.0)
- **[VERSION](VERSION)**: Current version number (single source of truth)
- **[docs/README.md](docs/README.md)**: Complete documentation index
- **[tests/README.md](tests/README.md)**: Testing guide
- **API Docs**: http://localhost:9528/docs (when server is running)

## 🔒 Security Features

- **Type Safety**: Pydantic models prevent type errors
- **Input Validation**: Automatic request validation
- **File Security**: Sanitized filenames and secure paths
- **Error Handling**: Structured error responses without sensitive info
- **Timeout Protection**: Configurable timeouts for external APIs
- **CORS**: Configurable CORS middleware

## 🚀 Performance

- **Async/Await**: Full async support for concurrent requests
- **Connection Pooling**: Efficient HTTP client management
- **Automatic Cleanup**: Scheduled cleanup of old images
- **GZip Compression**: Reduced response sizes
- **Fast Startup**: Optimized initialization

## 📈 Version History

### v2.2.0 (Current - 2025-10-22)
- Upgraded to wan2.5-t2i-preview for images (MINOR: significant model upgrade)
- Confirmed wan2.5-t2v-preview for videos
- Added VERSION file for version management
- Professional UI without emojis
- Project structure cleanup

### v2.1.0 (2025-01-21)
- Video generation support
- ReAct agent for intelligent routing
- Concurrency controls
- Complete async architecture

### v2.0.0 (Legacy)
- Complete FastAPI redesign
- Async/await throughout
- Modular architecture
- Type-safe with Pydantic

### v1.0.0 (Legacy - Removed)
- Flask-based implementation

See `CHANGELOG.md` for detailed version history.

## 📄 License

AGPLv3

## 👥 Support

For issues related to:
- **DashScope API**: Contact Alibaba Cloud support
- **Application**: Check logs and verify configuration
- **Installation**: Ensure all dependencies are installed
- **API Usage**: Refer to interactive docs at `/docs`

## 🙏 Acknowledgments

- Architecture inspired by MindGraph project
- Powered by Alibaba Cloud DashScope API
- Built with FastAPI framework

---

**Made with ❤️ by MindSpring Team | Author: lycosa9527**
