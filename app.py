import os
import json
import requests
import uuid
import logging
import time
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("INFO: Loaded environment variables from .env file")
except ImportError:
    print("INFO: python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or set environment variables manually.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['TEMP_FOLDER'] = 'temp_images'
app.config['DASHSCOPE_API_KEY'] = os.environ.get('DASHSCOPE_API_KEY', '')
# DashScope endpoints for Qwen models
app.config['QWEN_IMAGE_URL'] = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
app.config['QWEN_TURBO_URL'] = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

# Default image generation settings from environment variables
app.config['DEFAULT_IMAGE_SIZE'] = os.environ.get('DEFAULT_IMAGE_SIZE', '1664*928')
app.config['DEFAULT_WATERMARK'] = os.environ.get('DEFAULT_WATERMARK', 'false').lower() == 'true'
app.config['DEFAULT_PROMPT_EXTEND'] = os.environ.get('DEFAULT_PROMPT_EXTEND', 'false').lower() == 'true'
app.config['ENABLE_PROMPT_ENHANCEMENT'] = os.environ.get('ENABLE_PROMPT_ENHANCEMENT', 'true').lower() == 'true'

# Server configuration for image URLs
app.config['SERVER_HOST'] = os.environ.get('SERVER_HOST', 'localhost')
app.config['SERVER_PORT'] = os.environ.get('SERVER_PORT', '9528')

# Flask server binding configuration
app.config['FLASK_HOST'] = os.environ.get('FLASK_HOST', '0.0.0.0')
app.config['FLASK_PORT'] = int(os.environ.get('FLASK_PORT', '9528'))

# Timeout and performance settings
app.config['API_TIMEOUT'] = int(os.environ.get('API_TIMEOUT', '60'))  # seconds
app.config['IMAGE_DOWNLOAD_TIMEOUT'] = int(os.environ.get('IMAGE_DOWNLOAD_TIMEOUT', '30'))  # seconds
app.config['MAX_PROMPT_LENGTH'] = int(os.environ.get('MAX_PROMPT_LENGTH', '1000'))
app.config['MIN_PROMPT_LENGTH'] = int(os.environ.get('MIN_PROMPT_LENGTH', '3'))

# Debug mode configuration
app.config['DEBUG_MODE'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

# Ensure temp folder exists
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

def clean_temp_images_folder():
    """Clean all files from the temp images folder on application startup"""
    try:
        temp_folder = app.config['TEMP_FOLDER']
        if os.path.exists(temp_folder):
            # Get list of all files in temp folder
            files = [f for f in os.listdir(temp_folder) if os.path.isfile(os.path.join(temp_folder, f))]
            
            # Remove all files
            for file in files:
                file_path = os.path.join(temp_folder, file)
                try:
                    os.remove(file_path)
                    logger.info(f"Removed temp file: {file}")
                except OSError as e:
                    logger.warning(f"Failed to remove temp file {file}: {e}")
            
            logger.info(f"Cleaned temp images folder: {len(files)} files removed")
        else:
            logger.info("Temp images folder does not exist, skipping cleanup")
    except Exception as e:
        logger.error(f"Error cleaning temp images folder: {e}")

def validate_configuration():
    """Validate application configuration and provide helpful feedback"""
    issues = []
    
    if not app.config['DASHSCOPE_API_KEY']:
        issues.append("DASHSCOPE_API_KEY not set")
    
    if not os.path.exists(app.config['TEMP_FOLDER']):
        issues.append(f"TEMP_FOLDER '{app.config['TEMP_FOLDER']}' cannot be created")
    
    # Validate image size format
    valid_sizes = ["1664*928", "1472*1140", "1328*1328", "1140*1472", "928*1664"]
    if app.config['DEFAULT_IMAGE_SIZE'] not in valid_sizes:
        issues.append(f"DEFAULT_IMAGE_SIZE '{app.config['DEFAULT_IMAGE_SIZE']}' is not valid")
    
    return issues

def validate_prompt_basic(prompt):
    """
    Basic prompt validation - check length and ensure it's not empty.
    Returns (is_valid, reason) tuple.
    """
    # Check if prompt is empty or too short
    if not prompt or len(prompt.strip()) < app.config['MIN_PROMPT_LENGTH']:
        return False, f"Prompt is too short (min {app.config['MIN_PROMPT_LENGTH']} characters)"
    
    # Check if prompt is too long
    if len(prompt) > app.config['MAX_PROMPT_LENGTH']:
        return False, f"Prompt is too long (max {app.config['MAX_PROMPT_LENGTH']} characters)"
    
    return True, "Prompt is valid"

def enhance_prompt_for_k12_classroom(original_prompt):
    """
    Enhance simple prompts for K12 classroom use using Qwen Turbo via DashScope.
    Makes prompts more detailed, educational, and classroom-appropriate.
    """
    try:
        enhancement_prompt = f"""You are an expert K12 teacher and educational content creator specializing in creating engaging visual materials for classroom instruction.

Your task is to transform a simple image generation prompt into a detailed, educationally-focused description that will generate high-quality images perfect for K12 classroom use.

Original prompt: "{original_prompt}"

IMPORTANT SAFETY GUIDELINES - STRICTLY FOLLOW THESE RULES:
- ONLY create prompts for educational, classroom-appropriate content
- AVOID any controversial, political, religious, or sensitive topics
- NO violence, weapons, or harmful content
- NO adult content, explicit material, or inappropriate themes
- NO copyrighted characters, brands, or trademarked content
- NO content that could offend cultural or religious groups
- FOCUS on academic subjects, nature, science, art, and positive learning themes
- CRITICAL: The final generated image should contain NO text, words, letters, numbers, or written characters of any kind
- NO signs, labels, banners, posters with text, or any written content should appear in the image
- NO Chinese characters, English text, or any language symbols should be rendered
- Focus on visual elements only: objects, scenes, colors, shapes, and visual concepts
- If the prompt mentions text elements, describe the visual appearance without including the actual text content

Please enhance this prompt by following these educational guidelines:

1. **Educational Context**: Add subject-specific educational elements (science, math, history, language arts, etc.) that relate to the prompt
2. **Age-Appropriate Content**: Ensure the description is suitable for K12 students (elementary, middle, or high school level)
3. **Visual Learning Elements**: Include specific visual details that support learning objectives and make concepts clearer
4. **Classroom Environment**: Add context that makes the image feel like it belongs in an educational setting
5. **Engagement Factors**: Include elements that would capture student attention and interest
6. **Cultural Sensitivity**: Ensure the description is inclusive and appropriate for diverse classrooms
7. **Learning Objectives**: Structure the description to support specific educational outcomes

SAFE CONTENT CATEGORIES TO FOCUS ON:
- Natural science and biology (animals, plants, ecosystems)
- Mathematics and geometry concepts
- Art and creative expression
- Geography and landscapes
- Historical architecture and cultural artifacts
- Technology and innovation
- Environmental conservation
- Space and astronomy
- Weather and climate
- Food and nutrition (healthy choices)

Keep the enhanced prompt under 250 words and make it specific, descriptive, and educationally valuable.

Enhanced prompt:"""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {app.config["DASHSCOPE_API_KEY"]}'
        }
        
        payload = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": enhancement_prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.8
            }
        }
        
        logger.info("Enhancing prompt using Qwen Turbo via DashScope for K12 educational focus...")
        
        response = requests.post(
            app.config['QWEN_TURBO_URL'],
            headers=headers,
            json=payload,
            timeout=app.config['API_TIMEOUT']
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if 'output' in response_data and 'text' in response_data['output']:
                enhanced_prompt = response_data['output']['text'].strip()
                logger.info(f"Educational prompt enhancement completed via Qwen Turbo - Original: {len(original_prompt)} chars, Enhanced: {len(enhanced_prompt)} chars")
                return enhanced_prompt
            else:
                logger.warning("Unexpected response format from Qwen Turbo via DashScope, using original prompt")
                return original_prompt
        else:
            logger.warning(f"Qwen Turbo via DashScope API error - Status: {response.status_code}, using original prompt")
            return original_prompt
            
    except Exception as e:
        logger.warning(f"Prompt enhancement failed - Details: {str(e)}, using original prompt")
        return original_prompt

# Security: Input sanitization
def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks."""
    # Remove any path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Ensure it's a valid image extension
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        filename += '.jpg'
    return secure_filename(filename)

def validate_image_size(size_str):
    """Validate image size format and return normalized string."""
    valid_sizes = {
        "1664*928": "1664*928",   # 16:9
        "1472*1140": "1472*1140", # 4:3
        "1328*1328": "1328*1328", # 1:1 (default)
        "1140*1472": "1140*1472", # 3:4
        "928*1664": "928*1664"    # 9:16
    }
    return valid_sizes.get(size_str, "1664*928")

@app.route('/')
def index():
    """Home page with API documentation"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MindT2I - DashScope Image Generation API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin: 20px 0;
            }
            h1 {
                color: #4a5568;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .endpoint {
                background: #f7fafc;
                border-left: 4px solid #4299e1;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }
            .method {
                background: #4299e1;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 10px;
            }
            .url {
                background: #2d3748;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                margin: 10px 0;
            }
            .example {
                background: #edf2f7;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                color: #718096;
                font-size: 0.9em;
            }
            .debug-link {
                text-align: center;
                margin: 20px 0;
            }
            .debug-link a {
                display: inline-block;
                background: #48bb78;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 1.1em;
                transition: all 0.3s ease;
            }
            .debug-link a:hover {
                background: #38a169;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 MindT2I - DashScope Image Generation API</h1>
            
            <div class="debug-link">
                <a href="/debug">🧪 Try the Interactive Debug Tool</a>
            </div>
            
            <div class="endpoint">
                <div class="method">POST</div>
                <h3>Generate Image from Text</h3>
                <div class="url">/generate-image</div>
                <p>Generate images using Qwen Image via DashScope API</p>
                
                                 <div class="example">
                     <h4>Request Body:</h4>
                     <pre><code>{
     "prompt": "一只友好的猫在科学教室里，墙上挂着教育海报",
     "size": "1664*928",
     "negative_prompt": "",
     "watermark": false,
     "prompt_extend": false
 }</code></pre>
                 </div>
                
                                 <div class="example">
                     <h4>Response:</h4>
                     <pre><code>{
     "success": true,
     "image_url": "http://localhost:9528/temp_images/generated_20241201_143022_abc12345.jpg",
     "message": "Image generated successfully",
     "filename": "generated_20241201_143022_abc12345.jpg",
     "size": "1664*928",
     "prompt_enhanced": true,
     "original_prompt": "一只猫",
     "enhanced_prompt": "A friendly, educational illustration of a domestic cat in a bright, modern science classroom setting with educational posters on the walls, scientific equipment, and a welcoming atmosphere - no text or written content should appear in the image..."
 }</code></pre>
                 </div>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <h3>Get Generated Image</h3>
                <div class="url">/temp_images/&lt;filename&gt;</div>
                <p>Retrieve generated images from the temp folder</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <h3>Debug Tool</h3>
                <div class="url">/debug</div>
                <p>Interactive web interface for testing the API</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <h3>Health Check</h3>
                <div class="url">/health</div>
                <p>Check API health and system status</p>
            </div>
            
            <div class="example">
                <h4>Environment Variables Required:</h4>
                <p><strong>DASHSCOPE_API_KEY:</strong> Your DashScope API key</p>
                <p><strong>DEFAULT_IMAGE_SIZE:</strong> Default image size (default: 1664*928)</p>
                <p><strong>ENABLE_PROMPT_ENHANCEMENT:</strong> Enable Qwen Turbo enhancement (default: true)</p>
            </div>
            
            <div class="example">
                <h4>Security Features:</h4>
                <p>• Rate limiting: 10 requests per minute per IP</p>
                <p>• Input sanitization and validation</p>
                <p>• Path traversal protection</p>
                <p>• Automatic cleanup of old images (24h)</p>
                <p>• Structured error codes for better debugging</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Made by MindSpring Team | Author: lycosa9527</p>
        </div>
    </body>
    </html>
    '''

@app.route('/generate-image', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def generate_image():
    """Generate image using DashScope Qwen Image API with enhanced prompt processing."""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json',
                'error_code': 'INVALID_CONTENT_TYPE'
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data',
                'error_code': 'INVALID_JSON'
            }), 400

        # Extract and validate required fields
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required',
                'error_code': 'MISSING_PROMPT'
            }), 400

        # Basic prompt validation
        is_valid, validation_reason = validate_prompt_basic(prompt)
        if not is_valid:
            logger.warning(f"Prompt validation failed: {validation_reason}")
            return jsonify({
                'success': False, 
                'error': f'Prompt validation failed: {validation_reason}',
                'error_code': 'PROMPT_VALIDATION_FAILED'
            }), 400

        # Extract optional parameters with sensible defaults
        size = validate_image_size(data.get('size', app.config['DEFAULT_IMAGE_SIZE']))
        watermark = bool(data.get('watermark', app.config['DEFAULT_WATERMARK']))
        prompt_extend = bool(data.get('prompt_extend', app.config['DEFAULT_PROMPT_EXTEND']))
        negative_prompt = data.get('negative_prompt', '').strip()
        plain_text = data.get('plain_text', False)  # New parameter for plain text output

        # Store original prompt for response
        original_prompt = prompt

        # Enhanced prompt processing
        if app.config['ENABLE_PROMPT_ENHANCEMENT']:
            try:
                prompt = enhance_prompt_for_k12_classroom(prompt)
                logger.info(f"Educational prompt enhancement completed - Original: '{original_prompt[:50]}...', Enhanced: '{prompt[:50]}...'")
            except Exception as e:
                logger.error(f"Prompt enhancement failed: {str(e)}")
                # Continue with original prompt if enhancement fails
                prompt = original_prompt
                logger.info("Continuing with original prompt due to enhancement failure")

        # Check API key
        api_key = app.config['DASHSCOPE_API_KEY']
        if not api_key:
            logger.error("DashScope API key not configured")
            return jsonify({
                'success': False,
                'error': 'API key not configured',
                'error_code': 'API_KEY_MISSING'
            }), 500

        # Prepare request payload
        payload = {
            "model": "qwen-image",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": negative_prompt,
                "prompt_extend": prompt_extend,
                "watermark": watermark,
                "size": size
            }
        }

        # Make API request with timeout
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        logger.info(f"Sending request to DashScope Qwen Image API - Size: {size}, Watermark: {watermark}, Prompt Extend: {prompt_extend}")
        
        try:
            response = requests.post(
                app.config['QWEN_IMAGE_URL'],
                headers=headers,
                json=payload,
                timeout=app.config['API_TIMEOUT']
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("DashScope API request timed out")
            return jsonify({
                'success': False,
                'error': 'API request timed out',
                'error_code': 'API_TIMEOUT'
            }), 504
        except requests.exceptions.RequestException as e:
            logger.error(f"DashScope API request failed: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'API request failed: {str(e)}',
                'error_code': 'API_REQUEST_FAILED'
            }), 500

        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error("Failed to parse DashScope API response as JSON")
            return jsonify({
                'success': False,
                'error': 'Invalid response format from API',
                'error_code': 'INVALID_API_RESPONSE'
            }), 500

        # Check for API errors
        if response.status_code != 200:
            error_msg = response_data.get('message', 'Unknown API error')
            logger.error(f"DashScope API error {response.status_code}: {error_msg}")
            return jsonify({
                'success': False,
                'error': f'Qwen Image via DashScope API error: {response.status_code}',
                'details': error_msg,
                'error_code': 'API_ERROR'
            }), 500

        # Extract image URL from response
        try:
            image_url = response_data['output']['choices'][0]['message']['content'][0]['image']
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract image URL from response: {str(e)}")
            logger.error(f"Response structure: {json.dumps(response_data, indent=2)}")
            return jsonify({
                'success': False,
                'error': 'Invalid response format from Qwen Image via DashScope API',
                'error_code': 'INVALID_RESPONSE_FORMAT'
            }), 500

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"generated_{timestamp}_{unique_id}.jpg"
        
        # Sanitize filename for security
        safe_filename = sanitize_filename(filename)
        
        # Save image to temp folder
        try:
            image_response = requests.get(image_url, timeout=app.config['IMAGE_DOWNLOAD_TIMEOUT'])
            image_response.raise_for_status()
            
            image_path = os.path.join(app.config['TEMP_FOLDER'], safe_filename)
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Image saved successfully: {safe_filename}")
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to save generated image',
                'error_code': 'IMAGE_SAVE_FAILED'
            }), 500

        # Construct full image URL
        server_host = app.config.get('SERVER_HOST', 'localhost')
        server_port = app.config.get('SERVER_PORT', '9528')
        full_image_url = f"http://{server_host}:{server_port}/temp_images/{safe_filename}"

        # If plain text output is requested, return just the markdown image syntax
        if plain_text:
            markdown_text = f"![]({full_image_url})"
            logger.info(f"Image generation completed successfully - Returning plain text: {markdown_text}")
            return markdown_text, 200, {'Content-Type': 'text/plain'}

        # Success response (JSON format)
        response_data = {
            'success': True,
            'image_url': full_image_url,
            'markdown_image': f"![]({full_image_url})",
            'message': 'Image generated successfully',
            'filename': safe_filename,
            'size': size,
            'prompt_enhanced': app.config['ENABLE_PROMPT_ENHANCEMENT'],
            'original_prompt': original_prompt,
            'enhanced_prompt': prompt if app.config['ENABLE_PROMPT_ENHANCEMENT'] else None,
            'timestamp': timestamp,
            'request_id': str(uuid.uuid4())
        }

        logger.info(f"Image generation completed successfully - Filename: {safe_filename}, Size: {size}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error in generate_image: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@app.route('/generate-image-text', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def generate_image_text():
    """Generate image and return only the plain text markdown image syntax."""
    try:
        # Validate request content type
        if not request.is_json:
            return 'Content-Type must be application/json', 400, {'Content-Type': 'text/plain'}

        data = request.get_json()
        if not data:
            return 'Invalid JSON data', 400, {'Content-Type': 'text/plain'}

        # Extract and validate required fields
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return 'Prompt is required', 400, {'Content-Type': 'text/plain'}

        # Basic prompt validation
        is_valid, validation_reason = validate_prompt_basic(prompt)
        if not is_valid:
            logger.warning(f"Prompt validation failed: {validation_reason}")
            return f'Prompt validation failed: {validation_reason}', 400, {'Content-Type': 'text/plain'}

        # Extract optional parameters with validation
        size = validate_image_size(data.get('size', app.config['DEFAULT_IMAGE_SIZE']))
        watermark = bool(data.get('watermark', app.config['DEFAULT_WATERMARK']))
        prompt_extend = bool(data.get('prompt_extend', app.config['DEFAULT_PROMPT_EXTEND']))
        negative_prompt = data.get('negative_prompt', '').strip()

        # Store original prompt for response
        original_prompt = prompt

        # Enhanced prompt processing
        if app.config['ENABLE_PROMPT_ENHANCEMENT']:
            try:
                prompt = enhance_prompt_for_k12_classroom(prompt)
                logger.info(f"Educational prompt enhancement completed - Original: '{original_prompt[:50]}...', Enhanced: '{prompt[:50]}...'")
            except Exception as e:
                logger.error(f"Prompt enhancement failed: {str(e)}")
                # Continue with original prompt if enhancement fails
                prompt = original_prompt
                logger.info("Continuing with original prompt due to enhancement failure")

        # Check API key
        api_key = app.config['DASHSCOPE_API_KEY']
        if not api_key:
            logger.error("DashScope API key not configured")
            return 'API key not configured', 500, {'Content-Type': 'text/plain'}

        # Prepare request payload
        payload = {
            "model": "qwen-image",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "negative_prompt": negative_prompt,
                "prompt_extend": prompt_extend,
                "watermark": watermark,
                "size": size
            }
        }

        # Make API request with timeout
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        logger.info(f"Sending request to DashScope Qwen Image API for plain text output - Size: {size}, Watermark: {watermark}, Prompt Extend: {prompt_extend}")
        
        try:
            response = requests.post(
                app.config['QWEN_IMAGE_URL'],
                headers=headers,
                json=payload,
                timeout=app.config['API_TIMEOUT'] # Use API_TIMEOUT
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("DashScope API request timed out")
            return 'API request timed out', 504, {'Content-Type': 'text/plain'}
        except requests.exceptions.RequestException as e:
            logger.error(f"DashScope API request failed: {str(e)}")
            return f'API request failed: {str(e)}', 500, {'Content-Type': 'text/plain'}

        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error("Failed to parse DashScope API response as JSON")
            return 'Invalid response format from API', 500, {'Content-Type': 'text/plain'}

        # Check for API errors
        if response.status_code != 200:
            error_msg = response_data.get('message', 'Unknown API error')
            logger.error(f"DashScope API error {response.status_code}: {error_msg}")
            return f'Qwen Image via DashScope API error: {response.status_code}', response.status_code, {'Content-Type': 'text/plain'}

        # Extract image URL from response
        try:
            image_url = response_data['output']['choices'][0]['message']['content'][0]['image']
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract image URL from response: {str(e)}")
            logger.error(f"Response structure: {json.dumps(response_data, indent=2)}")
            return 'Invalid response format from Qwen Image via DashScope API', 500, {'Content-Type': 'text/plain'}

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"generated_{timestamp}_{unique_id}.jpg"
        
        # Sanitize filename for security
        safe_filename = sanitize_filename(filename)
        
        # Save image to temp folder
        try:
            image_response = requests.get(image_url, timeout=app.config['IMAGE_DOWNLOAD_TIMEOUT']) # Use IMAGE_DOWNLOAD_TIMEOUT
            image_response.raise_for_status()
            
            image_path = os.path.join(app.config['TEMP_FOLDER'], safe_filename)
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Image saved successfully: {safe_filename}")
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return 'Failed to save generated image', 500, {'Content-Type': 'text/plain'}

        # Construct full image URL
        server_host = app.config.get('SERVER_HOST', 'localhost')
        server_port = app.config.get('SERVER_PORT', '9528')
        full_image_url = f"http://{server_host}:{server_port}/temp_images/{safe_filename}"

        # Return only the plain text markdown image syntax
        markdown_text = f"![]({full_image_url})"
        logger.info(f"Image generation completed successfully - Returning plain text: {markdown_text}")
        return markdown_text, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        logger.error(f"Unexpected error in generate_image_text: {str(e)}", exc_info=True)
        return 'Internal server error', 500, {'Content-Type': 'text/plain'}

@app.route('/debug')
def debug_page():
    """Debug page for testing the API"""
    try:
        return send_from_directory('.', 'debug.html')
    except FileNotFoundError:
        return jsonify({'error': 'Debug page not found'}), 404

@app.route('/temp_images/<filename>')
def get_image(filename):
    """Serve generated images from temp folder with security validation"""
    # Sanitize filename to prevent path traversal
    safe_filename = sanitize_filename(filename)
    if safe_filename != filename:
        return jsonify({
            'success': False,
            'error': 'Invalid filename',
            'error_code': 'INVALID_FILENAME'
        }), 400
    
    # Check if file exists
    file_path = os.path.join(app.config['TEMP_FOLDER'], safe_filename)
    if not os.path.exists(file_path):
        return jsonify({
            'success': False,
            'error': 'Image not found',
            'error_code': 'IMAGE_NOT_FOUND'
        }), 404
    
    return send_from_directory(app.config['TEMP_FOLDER'], safe_filename)

def cleanup_old_images():
    """Clean up images older than 24 hours to prevent disk space issues"""
    try:
        current_time = time.time()
        max_age = 24 * 60 * 60  # 24 hours in seconds
        
        for filename in os.listdir(app.config['TEMP_FOLDER']):
            file_path = os.path.join(app.config['TEMP_FOLDER'], filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old image: {filename}")
    except Exception as e:
        logger.error(f"Error during image cleanup: {str(e)}")

# Schedule cleanup on startup
cleanup_old_images()

# Error handling middleware
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'error_code': 'ENDPOINT_NOT_FOUND'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'error_code': 'METHOD_NOT_ALLOWED'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'error_code': 'INTERNAL_ERROR'
    }), 500

@app.route('/config')
def get_config():
    """Get current application configuration (non-sensitive)"""
    return jsonify({
        'success': True,
        'config': {
            'default_image_size': app.config['DEFAULT_IMAGE_SIZE'],
            'default_watermark': app.config['DEFAULT_WATERMARK'],
            'default_prompt_extend': app.config['DEFAULT_PROMPT_EXTEND'],
            'prompt_enhancement_enabled': app.config['ENABLE_PROMPT_ENHANCEMENT'],
            'server_host': app.config['SERVER_HOST'],
            'server_port': app.config['SERVER_PORT'],
            'flask_host': app.config['FLASK_HOST'],
            'supported_image_sizes': [
                "1664*928", "1472*1140", "1328*1328", "1140*1472", "928*1664"
            ]
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint with detailed system status"""
    try:
        # Check temp folder accessibility
        temp_folder_accessible = os.access(app.config['TEMP_FOLDER'], os.W_OK)
        
        # Check if temp folder has space (cross-platform)
        try:
            if os.name == 'nt':  # Windows
                import shutil
                free_space_mb = shutil.disk_usage(app.config['TEMP_FOLDER']).free / (1024 * 1024)
            else:  # Unix/Linux
                temp_folder_stats = os.statvfs(app.config['TEMP_FOLDER'])
                free_space_mb = (temp_folder_stats.f_frsize * temp_folder_stats.f_bavail) / (1024 * 1024)
        except Exception:
            free_space_mb = 0.0
        
        # Count existing images
        try:
            image_count = len([f for f in os.listdir(app.config['TEMP_FOLDER']) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
        except OSError:
            image_count = 0
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'system': {
                'api_key_configured': bool(app.config['DASHSCOPE_API_KEY']),
                'temp_folder_accessible': temp_folder_accessible,
                'free_space_mb': round(free_space_mb, 2),
                'stored_images': image_count,
                'default_image_size': app.config['DEFAULT_IMAGE_SIZE'],
                'prompt_enhancement_enabled': app.config['ENABLE_PROMPT_ENHANCEMENT']
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Display ASCII banner
    print("=================================================================================")
    print("    ███╗   ███╗██╗███╗   ██╗██████╗ ███╗   ███╗ █████╗ ████████╗███████╗")
    print("    ████╗ ████║██║████╗  ██║██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝")
    print("    ██╔████╔██║██║██╔██╗ ██║██║  ██║██╔████╔██║███████║   ██║   █████╗  ")
    print("    ██║╚██╔╝██║██║██║╚██╗██║██║  ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  ")
    print("    ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗")
    print("    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝")
    print("=================================================================================")
    print("Made by MindSpring Team | Author: lycosa9527")
    print("")
    
    # Validate configuration
    config_issues = validate_configuration()
    if config_issues:
        print("WARNING: Configuration issues detected:")
        for issue in config_issues:
            print(f"   - {issue}")
        print("")
    
    # Check if API key is configured
    if not app.config['DASHSCOPE_API_KEY']:
        print("WARNING: DASHSCOPE_API_KEY environment variable not set!")
        print("   Please set your DashScope API key to use the image generation feature.")
        print("   Example: export DASHSCOPE_API_KEY='your_api_key_here'")
        print("")
    
    # Clean temp images folder on startup
    print("Cleaning temporary images folder...")
    clean_temp_images_folder()
    print("")
    
    print("Starting MindT2I Flask Application...")
    print(f"Server binding to: {app.config['FLASK_HOST']}:{app.config['FLASK_PORT']}")
    print(f"API Documentation available at: http://{app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}/")
    print(f"Debug Tool available at: http://{app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}/debug")
    print(f"Health check available at: http://{app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}/health")
    print("")
    
    # Run the application
    app.run(debug=app.config['DEBUG_MODE'], host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
