# MindT2I Documentation Index

Complete documentation for MindT2I v2.2.0 - AI-Powered Image & Video Generation for K12 Education

---

## 📖 Quick Links

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
- **[../README.md](../README.md)** - Main project documentation
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrate from Flask v1.0 to FastAPI v2.x

### API Documentation
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API reference with all endpoints, models, and schemas
- **[Swagger UI](http://localhost:9528/docs)** - Interactive API documentation (when server is running)
- **[ReDoc](http://localhost:9528/redoc)** - Alternative API documentation view

### Technical Guides
- **[CONCURRENCY_GUIDE.md](CONCURRENCY_GUIDE.md)** - Multi-user concurrency and scalability
- **[REACT_AGENT.md](REACT_AGENT.md)** - ReAct agent for intelligent image/video routing
- **[VIDEO_API_UPDATES.md](VIDEO_API_UPDATES.md)** - Video generation implementation details
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Comprehensive code review and improvement recommendations

### Reference
- **[KEYWORD_DETECTION.txt](KEYWORD_DETECTION.txt)** - Intent detection keyword reference
- **[../CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes
- **[../VERSION](../VERSION)** - Current version number

---

## 📚 Documentation by Topic

### For New Users

1. **[QUICKSTART.md](QUICKSTART.md)** - Installation and first image generation
2. **[../README.md](../README.md)** - Feature overview and basic usage
3. **[API_REFERENCE.md](API_REFERENCE.md)** - API endpoints and examples

### For Developers

1. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API specification
2. **[CONCURRENCY_GUIDE.md](CONCURRENCY_GUIDE.md)** - Handling concurrent requests
3. **[REACT_AGENT.md](REACT_AGENT.md)** - Understanding the ReAct agent
4. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Architecture and design patterns
5. **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code quality and improvement roadmap

### For Operations

1. **[CONCURRENCY_GUIDE.md](CONCURRENCY_GUIDE.md)** - Performance tuning
2. **[VIDEO_API_UPDATES.md](VIDEO_API_UPDATES.md)** - Video generation details
3. **[../tests/README.md](../tests/README.md)** - Testing and validation
4. **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code quality and best practices

---

## 🎯 By Use Case

### "I want to integrate MindT2I into my application"
→ Start with **[API_REFERENCE.md](API_REFERENCE.md)**
- Complete endpoint documentation
- Request/response schemas
- Code examples in multiple languages
- Error handling guide

### "I want to understand how it works"
→ Read **[REACT_AGENT.md](REACT_AGENT.md)** and **[CONCURRENCY_GUIDE.md](CONCURRENCY_GUIDE.md)**
- System architecture
- Intent detection mechanism
- Async/concurrent request handling

### "I'm migrating from v1.0"
→ Follow **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**
- Breaking changes
- New features
- Step-by-step migration

### "I need to generate videos"
→ Check **[VIDEO_API_UPDATES.md](VIDEO_API_UPDATES.md)**
- Video generation parameters
- Size and duration options
- Audio support

### "I'm having issues"
→ See **[API_REFERENCE.md](API_REFERENCE.md)** Troubleshooting section
- Common errors and solutions
- Log analysis
- Performance tips

---

## 📝 Document Descriptions

### API_REFERENCE.md
**Complete API reference documentation**
- All endpoints with request/response examples
- DashScope model integration details
- Error codes and handling
- Configuration reference
- Best practices and optimization
- Code examples in Python, JavaScript, cURL

### QUICKSTART.md
**Get started in 5 minutes**
- Installation steps
- Environment setup
- First image generation
- Basic usage examples

### MIGRATION_GUIDE.md
**Migrate from Flask to FastAPI**
- Version comparison
- Breaking changes
- New features
- Architecture changes
- Step-by-step migration

### CONCURRENCY_GUIDE.md
**Multi-user scalability**
- Async architecture
- Concurrent request handling
- Semaphore-based rate limiting
- Performance benchmarks
- Production deployment tips

### REACT_AGENT.md
**Intelligent routing system**
- How intent detection works
- Keyword-based classification
- Confidence scoring
- Fallback logic
- Customization guide

### VIDEO_API_UPDATES.md
**Video generation deep dive**
- wan2.5-t2v-preview details
- Size and resolution options
- Duration settings (5s/10s)
- Audio generation
- Task-based async pattern

### CODE_REVIEW.md
**Comprehensive code review and improvement roadmap**
- Code quality analysis
- Performance optimization opportunities
- Error handling improvements
- Testing recommendations
- Architecture enhancements
- Implementation priority guide

### KEYWORD_DETECTION.txt
**Intent detection reference**
- Complete keyword list
- Language support (English/Chinese)
- Detection logic
- Confidence levels

---

## 🔧 Configuration

All configuration is managed through `.env`:

```env
# See ../env.example for complete reference

# Key settings
DASHSCOPE_API_KEY=sk-xxx
IMAGE_MODEL=wan2.5-t2i-preview
VIDEO_MODEL=wan2.5-t2v-preview
QWEN_TEXT_MODEL=qwen-turbo
ENABLE_PROMPT_ENHANCEMENT=true
```

See **[API_REFERENCE.md](API_REFERENCE.md)** Configuration section for details.

---

## 🧪 Testing

See **[../tests/README.md](../tests/README.md)** for:
- Test suite documentation
- Running tests
- Test scenarios
- Performance testing

---

## 📊 Version Information

**Current Version**: See **[../VERSION](../VERSION)**  
**Change History**: See **[../CHANGELOG.md](../CHANGELOG.md)**

---

## 🤝 Contributing

When adding new features:
1. Update relevant documentation
2. Add API examples to **[API_REFERENCE.md](API_REFERENCE.md)**
3. Update **[../CHANGELOG.md](../CHANGELOG.md)**
4. Increment **[../VERSION](../VERSION)** following semantic versioning

---

## 📮 Support

For questions about:
- **API Usage**: See **[API_REFERENCE.md](API_REFERENCE.md)**
- **Integration**: Check **[Swagger UI](http://localhost:9528/docs)**
- **Errors**: See Troubleshooting sections
- **DashScope**: Visit [DashScope Documentation](https://help.aliyun.com/zh/model-studio/)

---

**Made with ❤️ by MindSpring Team | Author: lycosa9527**  
**MTEL Team from Educational Technology, Beijing Normal University**

