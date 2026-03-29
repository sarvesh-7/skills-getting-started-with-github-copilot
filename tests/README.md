# Tests

This directory contains comprehensive tests for the Mergington High School Activities API.

## Running Tests

### Basic Test Run
```bash
pytest tests/
```

### Verbose Output
```bash
pytest tests/ -v
```

### With Coverage Report
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### HTML Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
# View report in htmlcov/index.html
```

## Test Structure

- `conftest.py`: Pytest fixtures and configuration
- `test_app.py`: Comprehensive test suite covering:
  - GET /activities endpoint
  - POST /activities/{activity_name}/signup endpoint
  - DELETE /activities/{activity_name}/participants/{email} endpoint
  - Error cases and edge conditions
  - Data integrity tests

## Test Coverage

Current coverage: **100%** for `src/app.py`

The tests ensure:
- All API endpoints work correctly
- Proper error handling for invalid requests
- Data integrity is maintained
- Business logic is correctly implemented