# MindT2I - DashScope Image Generation API

A Flask-based web application that integrates with Alibaba Cloud's DashScope multimodal generation API to generate images from text prompts.

**Made by MindSpring Team | Author: lycosa9527**

## Features

- 🎨 **Text-to-Image Generation**: Convert Chinese and English text prompts into high-quality images
- 🧠 **AI-Powered Prompt Enhancement**: Automatically enhance simple prompts for K12 classroom use using Qwen Turbo
- 🌐 **RESTful API**: Clean, modern API endpoints for easy integration
- 💾 **Local Storage**: Generated images are saved locally in a temp folder
- 🔒 **Secure**: API key-based authentication with environment variables
- 📱 **Modern UI**: Beautiful, responsive web interface with API documentation
- ⚡ **Fast**: Optimized for quick image generation and retrieval

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

### 1. Home Page & Documentation
- **URL**: `/`
- **Method**: `GET`
- **Description**: Interactive API documentation with examples

## AI-Powered Educational Prompt Enhancement

The application automatically enhances simple prompts using **Qwen Turbo** to create detailed, educationally-focused image descriptions specifically designed for K12 classroom use.

### How It Works

1. **User Input**: Teacher provides a simple prompt (e.g., "a cat")
2. **AI Enhancement**: Qwen Turbo transforms the prompt with comprehensive educational focus including:
   - Subject-specific learning elements
   - Age-appropriate content for K12 students
   - Visual learning support details
   - Classroom environment context
   - Engagement and cultural sensitivity factors
3. **Enhanced Output**: Detailed prompt like "A scientifically accurate illustration of a domestic cat in a bright, modern science classroom setting, with clear anatomical features labeled for biology lessons, engaging expression that captures student interest, child-friendly art style suitable for elementary students, surrounded by educational elements like a microscope, science books, and a whiteboard with cat anatomy diagrams"
4. **Image Generation**: Enhanced prompt is sent to Qwen Image for high-quality, educationally-focused generation

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

### 2. Generate Image
- **URL**: `/generate-image`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body
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
- `prompt` (required): Text description for image generation
- `size` (optional): Image dimensions and aspect ratio (default: "1664*928")
  - `1664*928`: 16:9 (landscape) - **Default**
  - `1472*1140`: 4:3 (landscape) 
  - `1328*1328`: 1:1 (square)
  - `1140*1472`: 3:4 (portrait)
  - `928*1664`: 9:16 (portrait)
- `negative_prompt` (optional): What to avoid in the image
- `watermark` (optional): Add watermark (default: true)
- `prompt_extend` (optional): Extend prompt automatically (default: false, since we use Qwen Turbo for enhancement)

#### Response
```json
{
    "success": true,
    "image_url": "/temp_images/generated_20241201_143022_abc12345.jpg",
    "message": "Image generated successfully",
    "filename": "generated_20241201_143022_abc12345.jpg",
    "size": "1664*928",
    "prompt_enhanced": true,
    "original_prompt": "a cat",
    "enhanced_prompt": "A friendly, educational illustration of a domestic cat in a bright, colorful classroom setting, with clear anatomical features, engaging expression, and child-friendly art style suitable for K12 students"
}
```

### 3. Retrieve Generated Image
- **URL**: `/temp_images/<filename>`
- **Method**: `GET`
- **Description**: Download generated images

### 4. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Application status and configuration check

## Usage Examples

### cURL Example
```bash
curl --location 'http://localhost:9528/generate-image' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书"义本生知人机同道善思新"，右书"通云赋智乾坤启数高志远"， 横批"智启通义"，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
    "size": "1328*1328",
    "negative_prompt": "",
    "watermark": true
}'
```

### Python Example
```python
import requests
import json

url = "http://localhost:9528/generate-image"
payload = {
    "prompt": "A beautiful sunset over mountains with golden clouds",
    "size": "1664*928",  # 16:9 landscape
    "watermark": False
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    print(f"Image generated: {result['image_url']}")
else:
    print(f"Error: {response.text}")
```

### JavaScript Example
```javascript
const response = await fetch('http://localhost:9528/generate-image', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        prompt: "A serene Japanese garden with cherry blossoms",
        size: "1140*1472"  // 3:4 portrait
    })
});

const result = await response.json();
if (result.success) {
    console.log(`Image URL: ${result.image_url}`);
} else {
    console.error(`Error: ${result.error}`);
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
- `DEFAULT_WATERMARK`: Enable watermark by default (default: "true")
- `DEFAULT_PROMPT_EXTEND`: Enable prompt extension by default (default: "false", since we use Qwen Turbo for enhancement)
- `ENABLE_PROMPT_ENHANCEMENT`: Enable AI-powered educational prompt enhancement for K12 classroom use (default: "true")
- `FLASK_PORT`: Port to run the application on (default: 9528)
- `TEMP_FOLDER`: Folder to store generated images (default: temp_images)
- `LOG_LEVEL`: Logging level (default: INFO)

### Application Settings
- **Max file size**: 16MB
- **Temp folder**: `temp_images/`
- **API timeout**: 120 seconds for image generation
- **Port**: 9528 (configurable in app.py)

## File Structure
```
MindT2I/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── env.example        # Environment variables template
├── .env               # Your environment variables (create from env.example)
└── temp_images/       # Generated images storage (auto-created)
```

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Invalid request data
- API timeouts
- Network errors
- File I/O errors
- Invalid API responses

## Security Features

- Environment variable-based API key storage
- Input validation and sanitization
- Secure file handling
- Request size limits
- Comprehensive logging

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

## Support

For issues related to:
- **DashScope API**: Contact Alibaba Cloud support
- **Application**: Check the logs and ensure proper configuration
- **Image Generation**: Verify your API key and internet connection

## License

This project is developed by MindSpring Team. Please ensure compliance with DashScope API terms of service.

---

**Made with ❤️ by MindSpring Team | Author: lycosa9527**
