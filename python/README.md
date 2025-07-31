# Moderately AI Python SDK

The official Python SDK for the Moderately AI platform, providing easy access to content moderation and AI safety APIs.

## Features

- **Python 3.8+ Support**: Compatible with Python 3.8 and later versions
- **Type Safety**: Full type annotations with mypy support
- **Async/Await**: Built-in support for asynchronous operations
- **Error Handling**: Comprehensive exception handling for different error scenarios
- **Rate Limiting**: Built-in rate limit handling and retry logic
- **Modern Tooling**: Uses PDM for dependency management, Ruff for linting, and pytest for testing

## Installation

```bash
pip install moderatelyai-sdk
```

## Quick Start

```python
from moderatelyai_sdk import ModeratelyAIClient

# Initialize the client
client = ModeratelyAIClient(api_key="your-api-key")

# Moderate text content
result = client.moderate_content(
    content="Hello world!",
    content_type="text"
)

print(result)
# {'success': True, 'data': {'score': 0.1, 'flagged': False}}
```

## Usage

### Basic Content Moderation

```python
from moderatelyai_sdk import ModeratelyAIClient

client = ModeratelyAIClient(api_key="your-api-key")

# Moderate text
result = client.moderate_content("Some text to moderate")

if result["success"]:
    data = result["data"]
    if data["flagged"]:
        print(f"Content flagged with score: {data['score']}")
    else:
        print("Content is safe")
```

### Using Context Manager

```python
from moderatelyai_sdk import ModeratelyAIClient

with ModeratelyAIClient(api_key="your-api-key") as client:
    result = client.moderate_content("Text to check")
    print(result)
```

### Error Handling

```python
from moderatelyai_sdk import ModeratelyAIClient, APIError, AuthenticationError

client = ModeratelyAIClient(api_key="your-api-key")

try:
    result = client.moderate_content("Some content")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e.message}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

## Configuration

The client can be configured with various options:

```python
client = ModeratelyAIClient(
    api_key="your-api-key",
    base_url="https://api.moderately.ai",  # Custom API endpoint
    timeout=30,                            # Request timeout in seconds
    max_retries=3                          # Maximum retry attempts
)
```

## Development

This project uses PDM for dependency management. To set up the development environment:

```bash
# Install PDM
pip install pdm

# Install dependencies
pdm install

# Install pre-commit hooks
pdm run pre-commit install

# Run tests
pdm run pytest

# Run linting
pdm run ruff check .
pdm run ruff format .

# Type checking
pdm run mypy src/
```

## API Reference

### ModeratelyAIClient

The main client class for interacting with the Moderately AI API.

#### Methods

- `moderate_content(content: str, content_type: str = "text", options: Optional[Dict] = None) -> APIResponse`
- `get_status() -> APIResponse`

### Exceptions

- `ModeratelyAIError`: Base exception class
- `APIError`: Raised for API-related errors
- `AuthenticationError`: Raised for authentication failures
- `RateLimitError`: Raised when rate limits are exceeded
- `TimeoutError`: Raised for request timeouts
- `ValidationError`: Raised for input validation errors

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please visit our [GitHub repository](https://github.com/moderately-ai/platform-sdk) or contact us at sdk@moderately.ai.