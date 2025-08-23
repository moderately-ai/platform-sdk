# Moderately AI Python SDK - Claude Development Guide

## Quick Developer Setup

```bash
# Essential commands for immediate development
pdm install                     # Install all dependencies
pdm run pre-commit install     # Setup git hooks
pdm run pytest                 # Run tests
pdm run ruff check .           # Lint code
pdm run mypy src/              # Type check
```

## Project Overview

The Moderately AI Python SDK is a comprehensive client library for the Moderately AI platform, providing programmatic access to agents, datasets, pipelines, files, and team management. The SDK supports both synchronous and asynchronous operations with full type safety and rich error handling.

**Version**: 0.2.6  
**Python Support**: 3.8+  
**Package Manager**: PDM  
**API Base**: https://api.moderately.ai

## Key Features

- **Dual Client Support**: Both sync (`ModeratelyAI`) and async (`AsyncModeratelyAI`) clients
- **Rich Model Objects**: High-level model classes with domain-specific methods
- **Team-Scoped Operations**: Automatic filtering to user's team context
- **Type Safety**: Full type annotations with mypy support (Python 3.8+)
- **Comprehensive Error Handling**: Detailed exception hierarchy with retry logic
- **File Management**: Complete upload/download workflow with presigned URLs
- **Dataset Operations**: Data upload, schema management, and version control
- **Pipeline Execution**: Workflow configuration and execution monitoring

## Architecture

### Client Architecture

```
BaseClient (shared functionality)
├── ModeratelyAI (sync client)
└── AsyncModeratelyAI (async client)
```

Both clients provide identical APIs with automatic team-scoping via default query parameters:

- `client.team_id` - stored team ID for scoping
- Default query includes `teamIds: [team_id]` for list operations

### Resource Organization

```
resources/ (sync)          resources_async/ (async)
├── users.py              ├── users.py
├── teams.py              ├── teams.py
├── agents.py             ├── agents.py
├── agent_executions.py   ├── agent_executions.py
├── datasets.py           ├── datasets.py
├── files.py              ├── files.py
├── pipelines.py          ├── pipelines.py
├── pipeline_*.py         └── pipeline_*.py
```

### Model Layer

```
models/
├── _base.py                    # BaseModel foundation
├── dataset.py                  # DatasetModel + DatasetDataVersionModel
├── dataset_async.py            # Async variants
├── file.py                     # FileModel with rich operations
├── file_async.py               # FileAsyncModel
├── user.py                     # UserModel
└── pipeline*.py                # Pipeline-related models
```

Models provide rich functionality on top of raw API data:

- **DatasetModel**: upload_data(), download_data(), create_schema(), schema_builder()
- **FileModel**: download(), delete(), is_ready(), is_csv(), is_document(), etc.
- **UserModel**: Domain-specific user operations

## Development Environment

### Build System

- **PDM**: Package and dependency management
- **pyproject.toml**: Project configuration with build-backend = "pdm.backend"

### Code Quality

- **Ruff**: Linting and formatting (configured for Python 3.8+)
- **mypy**: Static type checking with strict configuration
- **pytest**: Testing framework with coverage reporting

### Development Workflow

```bash
# Daily development commands
pdm run ruff format .           # Format code (run first)
pdm run ruff check .            # Lint and fix issues
pdm run mypy src/               # Type check
pdm run pytest                 # Run tests
pdm run pytest --cov           # Coverage report

# Build and release
pdm build                       # Build distribution
pdm publish                     # Publish to PyPI (if configured)

# Useful for debugging
pdm run python -c "import moderatelyai_sdk; print(moderatelyai_sdk.__version__)"
```

### Environment Variables Required

```bash
export MODERATELY_API_KEY="your_api_key_here"
export MODERATELY_TEAM_ID="your_team_id_here"
```

## Core Implementation Patterns

### Client Initialization

```python
# Environment-based (recommended)
client = ModeratelyAI()  # Reads MODERATELY_API_KEY, MODERATELY_TEAM_ID

# Explicit configuration
client = ModeratelyAI(
    api_key="your_key",
    team_id="your_team",
    timeout=30.0,
    max_retries=3
)

# Context manager support
with ModeratelyAI() as client:
    # Client auto-closes HTTP connections
    pass
```

### Error Handling Hierarchy

```python
ModeratelyAIError (base)
├── APIError (HTTP errors with status codes)
│   ├── AuthenticationError (401/403)
│   ├── RateLimitError (429, includes retry_after)
│   ├── NotFoundError (404)
│   ├── ConflictError (409)
│   └── UnprocessableEntityError (422)
├── ValidationError (400 with field details)
└── TimeoutError (network timeouts)
```

### Retry Logic

Implemented in `BaseClient._request()` with configurable exponential backoff:

- Default: 3 retries with 2.0x backoff factor
- Retryable status codes: [429, 502, 503, 504]
- Automatic retry-after header handling for rate limits
- Network error retry with exponential backoff

### File Upload Workflow

Three-step presigned URL process abstracted into single `upload()` call:

1. **Request Upload URL**: `POST /files/upload-url` with file metadata
2. **Upload to S3**: `PUT` to presigned URL with file content
3. **Complete Upload**: `POST /files/{id}/complete` with verification data

```python
# Single SDK call handles entire workflow
file = client.files.upload(
    file="/path/to/file.pdf",
    name="Document",
    metadata={"category": "legal"}
)
```

### Dataset Operations

Rich dataset functionality with automatic schema inference:

```python
# Create dataset
dataset = client.datasets.create(name="Sales Data")

# Upload data with auto-detection
data_version = dataset.upload_data("sales.csv")

# Create schema from sample
schema = dataset.create_schema_from_sample("sales.csv")

# Fluent schema builder
schema = (dataset.schema_builder()
    .add_column("id", "int", required=True)
    .add_column("name", "string")
    .with_parsing(delimiter=",", header_row=1)
    .as_current()
    .create())
```

## Testing Approach

### Test Structure

```
tests/
├── test_client.py           # Client initialization and basic operations
├── test_async_client.py     # Async client functionality
└── test_*.py               # Resource-specific tests
```

### Testing Patterns

- **httpx mocking**: Mock HTTP client for unit tests
- **Fixture-based setup**: Common test data and client instances
- **Error scenario testing**: Comprehensive exception handling tests
- **Integration tests**: End-to-end workflow testing

## API Conventions

### Request/Response Patterns

- **Query parameters**: camelCase (e.g., `teamIds`, `pageSize`)
- **Request bodies**: camelCase JSON
- **Response data**: camelCase with pagination metadata
- **Model properties**: snake_case for Python conventions

### Pagination

Standard pagination structure:

```python
{
    "items": [...],           # Array of resource objects
    "pagination": {
        "page": 1,
        "page_size": 10,
        "total_items": 100,
        "total_pages": 10,
        "has_next_page": true
    }
}
```

## Quick Reference for Claude

### Key File Locations
- **Main clients**: `src/moderatelyai_sdk/client.py` & `client_async.py`
- **Resources**: `src/moderatelyai_sdk/resources/` (sync) & `resources_async/` (async)
- **Models**: `src/moderatelyai_sdk/models/` (rich domain objects)
- **Types**: `src/moderatelyai_sdk/types.py` (TypedDict definitions)
- **Exceptions**: `src/moderatelyai_sdk/exceptions.py` (error hierarchy)
- **Examples**: `examples/` (working code samples)
- **Tests**: `tests/` (pytest test suite)

### Making Changes
1. **Lint first**: `pdm run ruff format . && pdm run ruff check .`
2. **Type check**: `pdm run mypy src/`
3. **Test**: `pdm run pytest`
4. **Update version**: Bump in `src/moderatelyai_sdk/__init__.py`

### Common Patterns Found in Codebase
- All list operations automatically scope to `client.team_id`
- Rich models inherit from `BaseModel` in `models/_base.py`
- Error handling uses specific exception types from `exceptions.py`
- File uploads use 3-step presigned URL workflow (abstracted in SDK)
- Async variants mirror sync structure exactly with async/await

## Adding New Resources

### 1. Create Resource Class

```python
# resources/new_resource.py
from ._base import BaseResource
from ..models.new_model import NewModel

class NewResources(BaseResource):
    def list(self, **filters) -> List[NewModel]:
        response = self._get("/new-resources", options={"query": filters})
        return [NewModel(item, self._client) for item in response["items"]]

    def create(self, **data) -> NewModel:
        body = {"teamId": self._client.team_id, **data}
        response = self._post("/new-resources", body=body)
        return NewModel(response, self._client)
```

### 2. Create Model Class

```python
# models/new_model.py
from ._base import BaseModel

class NewModel(BaseModel):
    @property
    def resource_id(self) -> str:
        return self._data["resourceId"]

    def custom_operation(self) -> Any:
        return self._client._request(
            method="POST",
            path=f"/new-resources/{self.resource_id}/operation",
            cast_type=dict
        )
```

### 3. Add to Client

```python
# client.py (in __init__)
self.new_resources = NewResources(self)
```

### 4. Create Async Variants

- Copy resource to `resources_async/`
- Copy model to `models/new_model_async.py`
- Add async/await keywords to methods
- Update client initialization

## Best Practices

### Error Handling

- Always catch specific exceptions before general ones
- Use APIError.status_code and APIError.response_data for debugging
- Handle ValidationError.validation_details for field-level errors

### Resource Models

- Inherit from BaseModel for consistent behavior
- Use @property for data access with fallbacks
- Implement \_refresh() method for data updates
- Provide rich domain methods (is_ready(), download(), etc.)

### Type Safety

- Use TYPE_CHECKING imports to avoid circular dependencies
- Provide proper type hints for all public methods
- Use Optional[] for nullable fields
- Import models conditionally in methods when needed

### Performance

- Use context managers for automatic resource cleanup
- Batch API calls where possible
- Leverage model caching to avoid redundant requests
- Use async clients for I/O-bound operations

### Documentation

- Follow Google-style docstrings
- Provide usage examples in class/method docstrings
- Document parameter types and return values
- Include error scenarios in documentation

## Debugging Tips

### Common Issues
- **Import errors**: Check `__init__.py` exports in each module
- **Type errors**: Models expect camelCase API data but expose snake_case properties
- **Network errors**: Retry logic is built-in, check API key and team ID
- **File operations**: Use context managers to ensure proper cleanup

### Testing Specific Components
```bash
pdm run pytest tests/test_client.py -v           # Client tests
pdm run pytest tests/test_async_client.py -v     # Async tests
pdm run pytest -k "test_file" -v                 # File-related tests
pdm run pytest --cov-report=html                 # Coverage HTML report
```

### IDE Integration
- Configure mypy in your IDE for real-time type checking
- Set up ruff as your formatter and linter
- Use pytest as your test runner

This guide provides a comprehensive overview of the Moderately AI Python SDK architecture and development patterns. The codebase demonstrates excellent separation of concerns, comprehensive error handling, and rich domain modeling that makes the API easy to use.
