import os
import json
import requests
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import logging

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

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['TEMP_FOLDER'] = 'temp_images'
app.config['DASHSCOPE_API_KEY'] = os.environ.get('DASHSCOPE_API_KEY', '')
app.config['DASHSCOPE_BASE_URL'] = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
app.config['QWEN_TURBO_URL'] = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

# Default image generation settings from environment variables
app.config['DEFAULT_IMAGE_SIZE'] = os.environ.get('DEFAULT_IMAGE_SIZE', '1664*928')
app.config['DEFAULT_WATERMARK'] = os.environ.get('DEFAULT_WATERMARK', 'true').lower() == 'true'
app.config['DEFAULT_PROMPT_EXTEND'] = os.environ.get('DEFAULT_PROMPT_EXTEND', 'false').lower() == 'true'
app.config['ENABLE_PROMPT_ENHANCEMENT'] = os.environ.get('ENABLE_PROMPT_ENHANCEMENT', 'true').lower() == 'true'

# Ensure temp folder exists
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

def enhance_prompt_for_k12_classroom(original_prompt):
    """
    Enhance simple prompts for K12 classroom use using Qwen Turbo.
    Makes prompts more detailed, educational, and classroom-appropriate.
    """
    try:
        enhancement_prompt = f"""You are an expert K12 teacher and educational content creator specializing in creating engaging visual materials for classroom instruction.

Your task is to transform a simple image generation prompt into a detailed, educationally-focused description that will generate high-quality images perfect for K12 classroom use.

Original prompt: "{original_prompt}"

Please enhance this prompt by following these educational guidelines:

1. **Educational Context**: Add subject-specific educational elements (science, math, history, language arts, etc.) that relate to the prompt
2. **Age-Appropriate Content**: Ensure the description is suitable for K12 students (elementary, middle, or high school level)
3. **Visual Learning Elements**: Include specific visual details that support learning objectives and make concepts clearer
4. **Classroom Environment**: Add context that makes the image feel like it belongs in an educational setting
5. **Engagement Factors**: Include elements that would capture student attention and interest
6. **Cultural Sensitivity**: Ensure the description is inclusive and appropriate for diverse classrooms
7. **Learning Objectives**: Structure the description to support specific educational outcomes

Focus on creating a prompt that will generate images that teachers can use for:
- Lesson introductions and visual aids
- Student engagement and discussion starters
- Concept reinforcement and review
- Creative writing prompts and storytelling
- Cross-curricular connections

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
        
        logger.info("Enhancing prompt using Qwen Turbo for K12 educational focus...")
        
        response = requests.post(
            app.config['QWEN_TURBO_URL'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if 'output' in response_data and 'text' in response_data['output']:
                enhanced_prompt = response_data['output']['text'].strip()
                logger.info(f"Educational prompt enhancement completed - Original: {len(original_prompt)} chars, Enhanced: {len(enhanced_prompt)} chars")
                return enhanced_prompt
            else:
                logger.warning("Unexpected response format from Qwen Turbo, using original prompt")
                return original_prompt
        else:
            logger.warning(f"Qwen Turbo API error - Status: {response.status_code}, using original prompt")
            return original_prompt
            
    except Exception as e:
        logger.warning(f"Prompt enhancement failed - Details: {str(e)}, using original prompt")
        return original_prompt

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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 MindT2I - DashScope Image Generation API</h1>
            
            <div class="endpoint">
                <div class="method">POST</div>
                <h3>Generate Image from Text</h3>
                <div class="url">/generate-image</div>
                <p>Generate images using DashScope's multimodal generation API</p>
                
                <div class="example">
                    <h4>Request Body:</h4>
                    <pre><code>{
    "prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书"义本生知人机同道善思新"，右书"通云赋智乾坤启数高志远"， 横批"智启通义"，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
    "size": "1328*1328",
    "negative_prompt": "",
    "watermark": true
}</code></pre>
                </div>
                
                <div class="example">
                    <h4>Response:</h4>
                    <pre><code>{
    "success": true,
    "image_url": "/temp_images/abc123.jpg",
    "message": "Image generated successfully"
}</code></pre>
                </div>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <h3>Get Generated Image</h3>
                <div class="url">/temp_images/&lt;filename&gt;</div>
                <p>Retrieve generated images from the temp folder</p>
            </div>
            
            <div class="example">
                <h4>Environment Variables Required:</h4>
                <p><strong>DASHSCOPE_API_KEY:</strong> Your DashScope API key</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Made by MindSpring Team | Author: lycosa9527</p>
        </div>
    </body>
    </html>
    '''

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Generate image using DashScope API"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        # Enhance prompt for K12 classroom use if enabled
        original_prompt = prompt
        if app.config['ENABLE_PROMPT_ENHANCEMENT']:
            prompt = enhance_prompt_for_k12_classroom(prompt)
            logger.info(f"Educational prompt enhancement completed - Original: '{original_prompt[:50]}...', Enhanced: '{prompt[:50]}...'")
        
        # Check API key
        api_key = app.config['DASHSCOPE_API_KEY']
        if not api_key:
            return jsonify({'success': False, 'error': 'DASHSCOPE_API_KEY not configured'}), 500
        
        # Prepare request payload according to DashScope API specification
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
                "negative_prompt": data.get('negative_prompt', ''),
                "prompt_extend": data.get('prompt_extend', app.config['DEFAULT_PROMPT_EXTEND']),
                "watermark": data.get('watermark', app.config['DEFAULT_WATERMARK']),
                "size": data.get('size', app.config['DEFAULT_IMAGE_SIZE'])
            }
        }
        
        # Make request to DashScope API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        logger.info(f"DashScope API request initiated - Prompt: {prompt[:100]}...")
        
        response = requests.post(
            app.config['DASHSCOPE_BASE_URL'],
            headers=headers,
            json=payload,
            timeout=120  # 2 minutes timeout for image generation
        )
        
        if response.status_code != 200:
            logger.error(f"DashScope API error - Status: {response.status_code}, Response: {response.text}")
            return jsonify({
                'success': False, 
                'error': f'DashScope API error: {response.status_code}',
                'details': response.text
            }), 500
        
        # Parse response
        response_data = response.json()
        logger.info("DashScope API response processed successfully")
        
        # Extract image data
        if 'output' in response_data and 'images' in response_data['output']:
            images = response_data['output']['images']
            if images and len(images) > 0:
                image_data = images[0]
                
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"generated_{timestamp}_{unique_id}.jpg"
                filepath = os.path.join(app.config['TEMP_FOLDER'], filename)
                
                # Save image to temp folder
                if 'url' in image_data:
                    # If API returns a URL, download the image
                    img_response = requests.get(image_data['url'], timeout=30)
                    if img_response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                    else:
                        return jsonify({
                            'success': False, 
                            'error': 'Failed to download generated image'
                        }), 500
                elif 'base64' in image_data:
                    # If API returns base64 data
                    import base64
                    img_data = base64.b64decode(image_data['base64'])
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'No image data found in response'
                    }), 500
                
                # Return success response with image URL
                image_url = f"/temp_images/{filename}"
                logger.info(f"Image saved successfully - File: {filepath}")
                
                response_data = {
                    'success': True,
                    'image_url': image_url,
                    'message': 'Image generated successfully',
                    'filename': filename,
                    'size': data.get('size', app.config['DEFAULT_IMAGE_SIZE'])
                }
                
                # Include prompt information if enhancement was used
                if app.config['ENABLE_PROMPT_ENHANCEMENT']:
                    response_data['original_prompt'] = original_prompt
                    response_data['enhanced_prompt'] = prompt
                    response_data['prompt_enhanced'] = True
                else:
                    response_data['prompt_enhanced'] = False
                
                return jsonify(response_data)
            else:
                return jsonify({
                    'success': False, 
                    'error': 'No images generated'
                }), 500
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid response format from DashScope API'
            }), 500
            
    except requests.exceptions.Timeout:
        logger.error("DashScope API request timeout")
        return jsonify({
            'success': False, 
            'error': 'Request timeout - image generation is taking longer than expected'
        }), 408
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error - Details: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Request error: {str(e)}'
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error - Details: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/temp_images/<filename>')
def get_image(filename):
    """Serve generated images from temp folder"""
    try:
        return send_from_directory(app.config['TEMP_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_key_configured': bool(app.config['DASHSCOPE_API_KEY'])
    })

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
    
    # Check if API key is configured
    if not app.config['DASHSCOPE_API_KEY']:
        print("WARNING: DASHSCOPE_API_KEY environment variable not set!")
        print("   Please set your DashScope API key to use the image generation feature.")
        print("   Example: export DASHSCOPE_API_KEY='your_api_key_here'")
    
    print("Starting MindT2I Flask Application...")
    print("API Documentation available at: http://localhost:9528/")
    print("Health check available at: http://localhost:9528/health")
    
    app.run(debug=True, host='0.0.0.0', port=9528)
