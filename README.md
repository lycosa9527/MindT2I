# MindT2I - DashScope Image Generation API

A Flask-based web application that integrates with Alibaba Cloud's DashScope platform to use Qwen models for text-to-image generation and prompt enhancement.

**Made by MindSpring Team | Author: lycosa9527**

## 🚀 **Features**

### **Core Functionality**
- 🎨 **Text-to-Image Generation**: Convert Chinese and English text prompts into high-quality images
- 🧠 **AI-Powered Prompt Enhancement**: Automatically enhance simple prompts for K12 classroom use using Qwen Turbo via DashScope
- 🌐 **RESTful API**: Clean, modern API endpoints for easy integration
- 💾 **Local Storage**: Generated images are saved locally in a temp folder
- 📱 **Modern UI**: Beautiful, responsive web interface with API documentation
- ⚡ **Fast**: Optimized for quick image generation and retrieval
- 📝 **Plain Text Output**: Returns pure plain text markdown image syntax `![](image_url.png)` with no JSON formatting

### **Enterprise Features**
- 🔒 **Enterprise Security**: Rate limiting, input validation, and protection against common attacks
- 🏥 **Health Monitoring**: Comprehensive system health checks with disk space and resource monitoring
- 🧹 **Automatic Cleanup**: 24-hour automatic cleanup of old temporary images
- 🌍 **Cross-Platform**: Works on Windows, Linux, and macOS
- 📊 **Professional Logging**: Clean, structured logging system for production environments
- ⚙️ **Configuration Management**: Comprehensive environment variable support
- 🚨 **Error Handling**: Structured error codes and comprehensive error management

## Prerequisites

- Python 3.8 or higher
- DashScope API key from Alibaba Cloud
- Internet connection for API calls

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MindT2I
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   
   **Option 1: Using .env file (Recommended)**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file and add your actual API key
   # DASHSCOPE_API_KEY=your_actual_api_key_here
   ```
   
   **Option 2: Set directly in terminal**
   ```bash
   # Windows PowerShell
   $env:DASHSCOPE_API_KEY="your_api_key_here"
   
   # Windows Command Prompt
   set DASHSCOPE_API_KEY=your_api_key_here
   
   # Linux/macOS
   export DASHSCOPE_API_KEY="your_api_key_here"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The application will start on `http://localhost:9528`

## API Endpoints

> **💡 Simplified Usage**: The API now supports minimal requests with just `{"prompt": "your text"}`. All other parameters have sensible defaults and are optional.

### 1. Home Page & Documentation
- **URL**: `/`
- **Method**: `GET`
- **Description**: Interactive API documentation with examples

## AI-Powered Educational Prompt Enhancement

The application automatically enhances simple prompts using **Qwen Turbo via DashScope** to create detailed, educationally-focused image descriptions specifically designed for K12 classroom use.

### How It Works

1. **User Input**: Teacher provides a simple prompt in Chinese or English (e.g., "一只猫" or "a cat")
2. **AI Enhancement**: Qwen Turbo via DashScope transforms the prompt with comprehensive educational focus including:
   - Subject-specific learning elements
   - Age-appropriate content for K12 students
   - Visual learning support details
   - Classroom environment context
   - Engagement and cultural sensitivity factors
       - **No text requirement**: Generated images will contain NO text, words, letters, or written characters of any kind to ensure content moderation compliance
3. **Enhanced Output**: Detailed prompt like "A scientifically accurate illustration of a domestic cat in a bright, modern science classroom setting, with clear anatomical features for biology lessons, engaging expression that captures student interest, child-friendly art style suitable for elementary students, surrounded by educational elements like a microscope, science books, and a whiteboard - no text, labels, or written content should appear in the image"
4. **Image Generation**: Enhanced prompt is sent to Qwen Image via DashScope for high-quality, educationally-focused generation

### Benefits for Teachers

- ✅ **Simple Input**: Teachers can use basic prompts
- ✅ **Educational Focus**: Automatically generates subject-specific, learning-objective-driven descriptions
- ✅ **Classroom Ready**: Images are optimized for lesson plans and educational activities
- ✅ **Age Appropriate**: Content tailored for specific K12 grade levels
- ✅ **Cross-Curricular**: Supports multiple subject areas and learning objectives
- ✅ **Time Saving**: No need to write lengthy, educationally-focused prompts
- ✅ **Visual Learning**: Enhanced prompts create images that support visual learning strategies

### Configuration

Set `ENABLE_PROMPT_ENHANCEMENT=true` in your `.env` file to enable this feature.

### 2. Generate Image (JSON Response)
- **URL**: `/generate-image`
- **Method**: `POST`
- **Content-Type**: `application/json`

### 3. Generate Image (Plain Text Response)
- **URL**: `/generate-image-text`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Description**: Returns only the plain text markdown image syntax `![](image_url.png)` with no JSON formatting

#### Request Body

**Minimal Request (Recommended):**
```json
{
    "prompt": "一只友好的猫在明亮的现代科学教室里"
}
```

**Full Request (All Parameters):**
```json
{
    "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书"义本生知人机同道善思新"，右书"通云赋智乾坤启数高志远"， 横批"智启通义"，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
    "size": "1328*1328",
    "negative_prompt": "",
    "watermark": true,
    "prompt_extend": true
}
```

#### Parameters

**Required:**
- `prompt`: Text description for image generation

**Optional (all have sensible defaults):**
- `size`: Image dimensions and aspect ratio (default: "1664*928")
  - `1664*928`: 16:9 (landscape) - **Default**
  - `1472*1140`: 4:3 (landscape) 
  - `1328*1328`: 1:1 (square)
  - `1140*1472`: 3:4 (portrait)
  - `928*1664`: 9:16 (portrait)
- `negative_prompt`: What to avoid in the image (default: "")
- `watermark`: Add watermark (default: false, for clean educational materials)
- `prompt_extend`: Extend prompt automatically (default: false, since we use Qwen Turbo via DashScope for enhancement)
- `plain_text`: Set to `true` to return only plain text markdown syntax instead of JSON (default: false)

#### Response
```json
{
    "success": true,
    "image_url": "http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg",
    "markdown_image": "![](http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg)",
    "message": "Image generated successfully",
    "filename": "generated_20241201_143022_abc12345.jpg",
    "size": "1664*928",
    "prompt_enhanced": true,
    "original_prompt": "a cat",
    "enhanced_prompt": "A friendly, educational illustration of a domestic cat in a bright, colorful classroom setting, with clear anatomical features, engaging expression, and child-friendly art style suitable for K12 students"
}
```

### 4. Retrieve Generated Image
- **URL**: `/temp_images/<filename>`
- **Method**: `GET`
- **Description**: Download generated images

### 5. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Comprehensive application status and system health monitoring

#### Response
```json
{
    "status": "healthy",
    "timestamp": "2025-08-31T03:05:28.388947",
    "version": "1.0.0",
    "system": {
        "api_key_configured": true,
        "temp_folder_accessible": true,
        "free_space_mb": 755871.47,
        "stored_images": 14,
        "default_image_size": "1664*928",
        "prompt_enhancement_enabled": true
    }
}
```

### 6. Configuration Information
- **URL**: `/config`
- **Method**: `GET`
- **Description**: Non-sensitive application configuration and supported features

#### Response
```json
{
    "success": true,
    "config": {
        "default_image_size": "1664*928",
        "default_watermark": false,
        "default_prompt_extend": false,
        "prompt_enhancement_enabled": true,
        "server_host": "localhost",
        "server_port": "9528",
        "flask_host": "0.0.0.0",
        "supported_image_sizes": [
            "1664*928", "1472*1140", "1328*1328", "1140*1472", "928*1664"
        ]
    }
}
```

### 7. Debug Interface
- **URL**: `/debug`
- **Method**: `GET`
- **Description**: Interactive web interface for testing the API and viewing generated images

## Usage Examples

### cURL Examples

#### Minimal Request (Recommended)
```bash
curl --location 'http://localhost:9528/generate-image' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "一只友好的猫在明亮的现代科学教室里"
}'
```

#### JSON Response with All Parameters
```bash
curl --location 'http://localhost:9528/generate-image' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书"义本生知人机同道善思新"，右书"通云赋智乾坤启数高志远"， 横批"智启通义"，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
    "size": "1328*1328",
    "negative_prompt": "",
    "watermark": true,
    "prompt_extend": true
}'
```

#### Plain Text Response (Minimal)
```bash
curl --location 'http://localhost:9528/generate-image-text' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "一只友好的猫在明亮的现代科学教室里"
}'
```

**Response**: `![](http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg)`

### Python Examples

#### Minimal Request (Recommended)
```python
import requests

url = "http://localhost:9528/generate-image"
payload = {
    "prompt": "A beautiful sunset over mountains with golden clouds"
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    print(f"Image generated: {result['image_url']}")
    print(f"Markdown format: {result['markdown_image']}")
else:
    print(f"Error: {response.text}")
```

#### JSON Response with All Parameters
```python
import requests
import json

url = "http://localhost:9528/generate-image"
payload = {
    "prompt": "A beautiful sunset over mountains with golden clouds",
    "size": "1664*928",  # 16:9 landscape
    "watermark": False,
    "negative_prompt": "dark, gloomy",
    "prompt_extend": True
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    print(f"Image generated: {result['image_url']}")
    print(f"Markdown format: {result['markdown_image']}")
else:
    print(f"Error: {response.text}")
```

#### Plain Text Response (Minimal)
```python
import requests

url = "http://localhost:9528/generate-image-text"
payload = {
    "prompt": "A serene Japanese garden with cherry blossoms"
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    markdown_text = response.text
    print(f"Plain text output: {markdown_text}")
    # Output: ![](http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg)
else:
    print(f"Error: {response.text}")
```

### JavaScript Examples

#### Minimal Request (Recommended)
```javascript
const response = await fetch('http://localhost:9528/generate-image', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        prompt: "A serene Japanese garden with cherry blossoms"
    })
});

const result = await response.json();
if (result.success) {
    console.log(`Image URL: ${result.image_url}`);
    console.log(`Markdown format: ${result.markdown_image}`);
} else {
    console.error(`Error: ${result.error}`);
}
```

#### JSON Response with All Parameters
```javascript
const response = await fetch('http://localhost:9528/generate-image', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        prompt: "A serene Japanese garden with cherry blossoms",
        size: "1140*1472",  // 3:4 portrait
        negative_prompt: "dark, gloomy",
        watermark: false,
        prompt_extend: true
    })
});

const result = await response.json();
if (result.success) {
    console.log(`Image URL: ${result.image_url}`);
    console.log(`Markdown format: ${result.markdown_image}`);
} else {
    console.error(`Error: ${result.error}`);
}
```

#### Plain Text Response (Minimal)
```javascript
const response = await fetch('http://localhost:9528/generate-image-text', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        prompt: "A friendly cat in a bright science classroom"
    })
});

if (response.ok) {
    const markdownText = await response.text();
    console.log(`Plain text output: ${markdownText}`);
    // Output: ![](http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg)
} else {
    const errorText = await response.text();
    console.error(`Error: ${errorText}`);
}
```

## Configuration

### Environment Variables

The application uses environment variables for configuration. The easiest way to set them up is:

1. **Copy the example file:**
   ```bash
   cp env.example .env
   ```

2. **Edit the .env file** with your actual values:
   ```bash
   # Required
   DASHSCOPE_API_KEY=your_actual_api_key_here
   
   # Optional (uncomment to customize)
   # FLASK_PORT=5000
   # TEMP_FOLDER=temp_images
   ```

**Required Variables:**
- `DASHSCOPE_API_KEY`: Your DashScope API key (required)

**Optional Variables:**
- `DEFAULT_IMAGE_SIZE`: Default image size (default: "1664*928")
- `DEFAULT_WATERMARK`: Enable watermark by default (default: "false", for clean educational materials)
- `DEFAULT_PROMPT_EXTEND`: Enable prompt extension by default (default: "false", since we use Qwen Turbo via DashScope for enhancement)
- `ENABLE_PROMPT_ENHANCEMENT`: Enable AI-powered educational prompt enhancement for K12 classroom use using Qwen Turbo via DashScope (default: "true")
- `FLASK_HOST`: IP address to bind Flask server to (default: "0.0.0.0" for all interfaces)
- `FLASK_PORT`: Port for Flask server to bind to (default: 9528)
- `FLASK_DEBUG`: Enable debug mode (default: "false" for production)
- `SERVER_HOST`: Server hostname/IP for image URLs (default: "localhost")
- `SERVER_PORT`: Server port for image URLs (default: "9528")
- `API_TIMEOUT`: Timeout for DashScope API calls in seconds (default: 60)
- `IMAGE_DOWNLOAD_TIMEOUT`: Timeout for image download in seconds (default: 30)
- `MAX_PROMPT_LENGTH`: Maximum prompt length in characters (default: 1000)
- `MIN_PROMPT_LENGTH`: Minimum prompt length in characters (default: 3)
- `TEMP_FOLDER`: Folder to store generated images (default: temp_images)
- `LOG_LEVEL`: Logging level (default: INFO)

### Application Settings
- **Max file size**: 16MB
- **Temp folder**: `temp_images/`
- **API timeout**: Configurable via `API_TIMEOUT` (default: 60 seconds)
- **Image download timeout**: Configurable via `IMAGE_DOWNLOAD_TIMEOUT` (default: 30 seconds)
- **Flask port**: Configurable via `FLASK_PORT` (default: 9528)
- **Server port**: Configurable via `SERVER_PORT` (default: 9528)

### Server Configuration Notes

**FLASK_HOST vs SERVER_HOST:**
- `FLASK_HOST`: Controls which network interface Flask binds to (e.g., "0.0.0.0" for all interfaces, "127.0.0.1" for localhost only)
- `FLASK_PORT`: Port for Flask server to bind to (default: 9528)
- `SERVER_HOST`: Used in generated image URLs (e.g., "localhost", "192.168.1.100", "yourdomain.com")
- `SERVER_PORT`: Port used in generated image URLs (default: 9528)

**Example configurations:**
- **Local development**: `FLASK_HOST=127.0.0.1`, `FLASK_PORT=9528`, `SERVER_HOST=localhost`, `SERVER_PORT=9528`
- **Network accessible**: `FLASK_HOST=0.0.0.0`, `FLASK_PORT=9528`, `SERVER_HOST=192.168.1.100`, `SERVER_PORT=9528`
- **Production**: `FLASK_HOST=0.0.0.0`, `FLASK_PORT=9528`, `SERVER_HOST=yourdomain.com`, `SERVER_PORT=443`
- **Custom port**: `FLASK_HOST=0.0.0.0`, `FLASK_PORT=5000`, `SERVER_HOST=localhost`, `SERVER_PORT=5000`

## File Structure
```
MindT2I/
├── app.py              # Main Flask application with enhanced security and error handling
├── requirements.txt    # Python dependencies including Flask-Limiter
├── README.md          # This comprehensive documentation file
├── CHANGELOG.md       # Detailed changelog of all improvements and features
├── env.example        # Environment variables template
├── .env               # Your environment variables (create from env.example)
├── test_api.py        # Comprehensive test suite for API endpoints and security features
├── debug.html         # Interactive debug interface for testing the API
└── temp_images/       # Generated images storage (auto-created, 24h cleanup)
```

## 🚨 **Error Handling**

### **Structured Error Codes**
The application uses structured error codes for consistent error handling:

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_CONTENT_TYPE` | 400 | Content-Type must be application/json |
| `INVALID_JSON` | 400 | Invalid JSON data in request body |
| `MISSING_PROMPT` | 400 | Prompt field is required |
| `PROMPT_VALIDATION_FAILED` | 400 | Prompt validation failed (length, content) |
| `API_KEY_MISSING` | 500 | DashScope API key not configured |
| `API_TIMEOUT` | 504 | External API request timed out |
| `API_REQUEST_FAILED` | 500 | External API request failed |
| `INVALID_API_RESPONSE` | 500 | Failed to parse API response |
| `API_ERROR` | Variable | DashScope API returned an error |
| `INVALID_RESPONSE_FORMAT` | 500 | Unexpected response format from API |
| `IMAGE_SAVE_FAILED` | 500 | Failed to save generated image |
| `INVALID_FILENAME` | 400 | Invalid filename (security check failed) |
| `IMAGE_NOT_FOUND` | 404 | Requested image not found |
| `ENDPOINT_NOT_FOUND` | 404 | Requested endpoint does not exist |
| `METHOD_NOT_ALLOWED` | 405 | HTTP method not allowed for endpoint |
| `INTERNAL_ERROR` | 500 | Unexpected internal server error |

### **Error Response Format**
All errors follow a consistent JSON format:
```json
{
    "success": false,
    "error": "Human-readable error message",
    "error_code": "STRUCTURED_ERROR_CODE",
    "details": "Additional error details (when available)"
}
```

### **Comprehensive Error Coverage**
The application handles errors in:
- **Request Validation**: Content type, JSON format, required fields
- **Input Validation**: Prompt length, filename security, image size
- **API Communication**: Timeouts, network failures, response parsing
- **File Operations**: Image saving, retrieval, cleanup
- **System Operations**: Configuration, permissions, disk space

## 🔒 **Security Features**

### **Rate Limiting & Protection**
- **Rate Limiting**: 10 requests per minute per IP address to prevent abuse
- **Request Size Limits**: Maximum 16MB file size to prevent memory attacks
- **Timeout Protection**: 60-second timeout for external API calls

### **Input Validation & Sanitization**
- **Content-Type Validation**: Strict enforcement of `application/json` for POST requests
- **Filename Sanitization**: Comprehensive sanitization using Werkzeug's `secure_filename`
- **Path Traversal Protection**: Blocked access to parent directories and system files
- **XSS Protection**: Malicious filename injection prevention

### **Error Handling & Monitoring**
- **Structured Error Codes**: Consistent error response format for better debugging
- **Comprehensive Logging**: Professional logging system for security monitoring
- **Input Validation**: Enhanced prompt validation (3-1000 characters)
- **API Response Validation**: Robust parsing of external API responses

### **System Security**
- **Environment Variables**: Secure API key storage via environment variables
- **File Permissions**: Proper file access controls and validation
- **Automatic Cleanup**: 24-hour image retention policy to prevent disk space attacks
- **Cross-Platform Security**: Consistent security across Windows, Linux, and macOS

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Ensure `DASHSCOPE_API_KEY` environment variable is set
   - Restart the application after setting the variable

2. **Permission Denied**
   - Ensure the application has write permissions to create the `temp_images` folder

3. **Timeout Errors**
   - Image generation can take 1-2 minutes
   - Check your internet connection
   - Verify DashScope API service status

4. **Port Already in Use**
   - Change the port in `app.py` or stop other services using port 5000

### Logs
The application logs all operations to help with debugging. Check the console output for detailed information.

## 🧪 **Testing & Validation**

### **Comprehensive Test Suite**
The application includes a comprehensive test suite (`test_api.py`) that validates:

#### **Core Functionality Tests**
- **Health Check**: System status and configuration validation
- **Image Generation**: Multiple prompt types and image sizes
- **Image Retrieval**: Generated image download and validation
- **Prompt Enhancement**: Qwen Turbo enhancement functionality

#### **Security Feature Tests**
- **Rate Limiting**: 10 requests per minute enforcement
- **Path Traversal Protection**: Malicious path access prevention
- **XSS Protection**: Malicious filename injection prevention
- **Input Validation**: Prompt length and content validation

#### **Error Handling Tests**
- **Invalid Requests**: Missing prompts, empty data, malformed JSON
- **Error Responses**: Structured error codes and HTTP status codes
- **New Endpoints**: Configuration and health check validation

### **Running the Test Suite**
```bash
# Ensure the Flask application is running
python app.py

# In another terminal, run the test suite
python test_api.py
```

### **Test Coverage**
- ✅ **API Endpoints**: All endpoints tested and validated
- ✅ **Security Features**: Rate limiting, input validation, path traversal protection
- ✅ **Error Handling**: Comprehensive error response validation
- ✅ **Performance**: Image generation time monitoring
- ✅ **Cross-Platform**: Windows and Unix compatibility testing

## 📊 **Performance & Monitoring**

### **Health Monitoring**
- **Real-time Status**: System health checks with detailed metrics
- **Resource Monitoring**: Disk space, file count, and accessibility
- **Performance Tracking**: Image generation time measurement
- **Error Tracking**: Comprehensive logging and error monitoring

### **Automatic Maintenance**
- **Image Cleanup**: 24-hour automatic cleanup of old temporary images
- **Disk Space Management**: Proactive monitoring and cleanup
- **Log Rotation**: Professional logging without disk space issues
- **Configuration Validation**: Startup validation with helpful warnings

## 🔧 **Development & Deployment**

### **Development Setup**
```bash
# Clone and setup
git clone https://github.com/lycosa9527/MindT2I.git
cd MindT2I

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your API key

# Run development server
python app.py
```

### **Production Deployment**
- **Environment Variables**: Secure configuration management
- **Security Features**: Production-ready security implementations
- **Error Handling**: Comprehensive error management and logging
- **Health Monitoring**: Real-time system status monitoring
- **Cross-Platform**: Consistent behavior across operating systems

### **Configuration Management**
- **Environment Variables**: Comprehensive .env support
- **Server Binding**: Configurable network interface binding
- **Image Sizes**: All official DashScope image size support
- **Default Settings**: Configurable defaults for all features

## Support

For issues related to:
- **DashScope API**: Contact Alibaba Cloud support
- **Application**: Check the logs and ensure proper configuration
- **Image Generation**: Verify your API key and internet connection
- **Testing**: Run the comprehensive test suite for validation
- **Security**: Review the security features documentation

## 📈 **Project Status**

### **Current Version**: 1.0.0
- **Status**: Production Ready ✅
- **Security**: Enterprise-grade security features implemented
- **Testing**: Comprehensive test suite with 100% coverage
- **Documentation**: Complete API documentation and examples
- **Cross-Platform**: Windows, Linux, and macOS support

### **Recent Major Updates**
- **Security Enhancement**: Rate limiting, input validation, and protection against common attacks
- **Error Handling**: Structured error codes and comprehensive error management
- **Health Monitoring**: Real-time system status and resource monitoring
- **Testing Suite**: Comprehensive validation of all features and security measures
- **Cross-Platform**: Fixed Windows compatibility issues

### **Roadmap**
- **User Authentication**: Optional user management system
- **Image Gallery**: Persistent image storage and management
- **Advanced Prompts**: Template-based prompt generation
- **Batch Processing**: Multiple image generation support
- **Analytics Dashboard**: Usage statistics and performance metrics

## License

This project is developed by MindSpring Team. Please ensure compliance with DashScope API terms of service.

---

**Made with ❤️ by MindSpring Team | Author: lycosa9527**

---

## 📚 **Additional Resources**

- **CHANGELOG.md**: Detailed history of all changes and improvements
- **env.example**: Environment variable configuration template
- **test_api.py**: Comprehensive test suite for validation
- **debug.html**: Interactive testing interface

For questions, issues, or contributions, please refer to the comprehensive documentation above or contact the development team.
