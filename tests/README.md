# Tests

This directory contains test scripts for MindT2I.

## Test Files

### `test_concurrent.py`
Tests concurrent video generation with multiple users.

```bash
# Quick test (3 users)
python tests/test_concurrent.py

# Stress test (10 users)
python tests/test_concurrent.py stress

# Maximum load test (25 users)
python tests/test_concurrent.py max
```

### `test_fastapi.py`
Tests FastAPI endpoints and basic functionality.

```bash
python tests/test_fastapi.py
```

### `test_react_agent.py`
Tests the keyword detection and intent routing.

```bash
python tests/test_react_agent.py
```

### `test_video.py`
Tests video generation endpoints.

```bash
python tests/test_video.py
```

## Running Tests

Make sure the server is running before running tests:

```bash
# Start server
python main.py

# In another terminal, run tests
python tests/test_concurrent.py
```

