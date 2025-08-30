# Changelog

All notable changes to the MindT2I project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-31

### 🚀 **Major Features & Improvements**

#### **Security & Security Features**
- **Rate Limiting**: Implemented Flask-Limiter with 10 requests per minute per IP address
- **Input Sanitization**: Added comprehensive filename sanitization to prevent path traversal attacks
- **XSS Protection**: Enhanced filename validation to block malicious script injection attempts
- **Path Traversal Protection**: Implemented robust protection against directory traversal attacks
- **Structured Error Codes**: Added comprehensive error handling with specific error codes for better debugging

#### **Enhanced API Endpoints**
- **New `/health` Endpoint**: Comprehensive system health check with disk space, image count, and configuration status
- **New `/config` Endpoint**: Non-sensitive configuration information including supported image sizes and settings
- **Enhanced Error Handling**: Global error handlers for 404, 405, and 500 errors with structured JSON responses
- **Improved `/generate-image`**: Enhanced validation, timeout handling, and robust error management

#### **Code Quality & Architecture**
- **Modular Functions**: Refactored code into focused, testable functions
- **Configuration Validation**: Startup validation with helpful warning messages
- **Cross-Platform Compatibility**: Fixed Windows-specific issues (os.statvfs compatibility)
- **Automatic Cleanup**: 24-hour automatic cleanup of old temporary images
- **Professional Logging**: Clean, structured logging system without emojis

#### **Testing & Validation**
- **Comprehensive Test Suite**: Added extensive testing for security features, error handling, and API endpoints
- **Security Testing**: Tests for rate limiting, path traversal, and XSS protection
- **Error Handling Tests**: Validation of structured error responses and error codes
- **Performance Monitoring**: Generation time tracking and system health monitoring

### 🔧 **Technical Improvements**

#### **Error Handling & Validation**
- **Content-Type Validation**: Strict JSON content type enforcement
- **Input Validation**: Enhanced prompt validation with length checks (3-1000 characters)
- **API Response Parsing**: Robust parsing of DashScope API responses with fallback handling
- **Timeout Management**: 60-second timeout for API requests with proper error handling

#### **Security Functions**
- **`sanitize_filename()`**: Comprehensive filename sanitization using Werkzeug's secure_filename
- **`validate_image_size()`**: Image size validation with fallback to default
- **`validate_prompt_basic()`**: Streamlined prompt validation focusing on length and content

#### **Configuration Management**
- **Environment Variables**: Comprehensive .env support for all configurable options
- **Server Binding**: Configurable Flask host binding via FLASK_HOST environment variable
- **Image Size Configuration**: Support for all official DashScope image sizes (16:9, 4:3, 1:1, 3:4, 9:16)
- **Default Settings**: Configurable defaults for watermark, prompt enhancement, and image sizes

### 📚 **Documentation Updates**
- **API Documentation**: Enhanced HTML documentation with security features and examples
- **Security Features Section**: Detailed documentation of implemented security measures
- **Error Code Reference**: Comprehensive list of structured error codes and their meanings
- **Configuration Guide**: Detailed environment variable configuration instructions

### 🧪 **Testing Enhancements**
- **Security Feature Tests**: Rate limiting, path traversal, and XSS protection validation
- **Error Handling Tests**: 404, 405, and invalid request handling validation
- **New Endpoint Tests**: Configuration and health check endpoint validation
- **Performance Tests**: Image generation and retrieval performance monitoring

### 🔒 **Security Features Implemented**
1. **Rate Limiting**: 10 requests per minute per IP address
2. **Input Sanitization**: Comprehensive filename and input validation
3. **Path Traversal Protection**: Blocked access to parent directories
4. **XSS Protection**: Malicious filename injection prevention
5. **Content-Type Validation**: Strict JSON enforcement
6. **Automatic Cleanup**: 24-hour image retention policy
7. **Structured Error Codes**: Consistent error response format

### 🌐 **Cross-Platform Support**
- **Windows Compatibility**: Fixed os.statvfs issues using shutil.disk_usage
- **Linux/Unix Support**: Maintained compatibility with Unix-based systems
- **Environment Variables**: Cross-platform .env file support

### 📊 **Performance & Monitoring**
- **Health Monitoring**: Real-time system status and resource monitoring
- **Performance Tracking**: Image generation time measurement
- **Resource Management**: Automatic disk space monitoring and cleanup
- **Error Tracking**: Comprehensive error logging and monitoring

### 🔄 **Backward Compatibility**
- **API Endpoints**: All existing endpoints maintained with enhanced functionality
- **Response Format**: Enhanced responses with additional metadata while maintaining core structure
- **Configuration**: Default values ensure existing setups continue to work

---

## [0.9.0] - 2025-08-30

### 🎯 **Core Features**
- **Flask Application**: Basic Flask web application for image generation
- **DashScope Integration**: Qwen Image and Qwen Turbo API integration
- **Prompt Enhancement**: K12-focused educational prompt enhancement system
- **Image Storage**: Temporary image storage with unique filename generation
- **Basic API**: POST /generate-image endpoint for image generation

### 🔧 **Initial Implementation**
- **Environment Configuration**: .env file support for API keys and settings
- **Debug Interface**: HTML debug page for testing and visualization
- **Basic Validation**: Simple prompt and parameter validation
- **Image Retrieval**: GET /temp_images/<filename> endpoint for image access

### 📚 **Documentation**
- **README.md**: Basic setup and usage instructions
- **API Examples**: Curl examples and response format documentation
- **Configuration Guide**: Environment variable setup instructions

---

## [0.8.0] - 2025-08-29

### 🚀 **Foundation**
- **Project Initialization**: Git repository setup and initial commit
- **Basic Structure**: Core application architecture and file organization
- **Dependencies**: Requirements.txt with essential Python packages
- **Configuration**: Basic application configuration and settings

---

## **Unreleased**

### 🔮 **Planned Features**
- **User Authentication**: Optional user management system
- **Image Gallery**: Persistent image storage and management
- **Advanced Prompts**: Template-based prompt generation
- **Batch Processing**: Multiple image generation support
- **Analytics Dashboard**: Usage statistics and performance metrics

---

## **Contributing**

This changelog is maintained by the MindSpring Team. For questions or contributions, please contact the development team.

---

**Made by MindSpring Team | Author: lycosa9527**
