# Moderately AI Platform SDK

Official SDKs for the Moderately AI platform, providing programmatic access to agents, datasets, pipelines, and team management.

## Available SDKs

### Python SDK

The Python SDK is located in the `python/` directory and provides:

- **Team-scoped operations**: Automatic filtering and scoping to your team
- **Resource management**: Agents, datasets, pipelines, files, and users
- **Type safety**: Full type annotations with mypy support
- **Async support**: Both synchronous and asynchronous clients
- **Modern tooling**: Built with httpx, PDM, and pytest

**Quick Start:**

```python
import moderatelyai_sdk

# Initialize with environment variables
client = moderatelyai_sdk.ModeratelyAI()  # reads MODERATELY_API_KEY and MODERATELY_TEAM_ID

# Or with explicit parameters
client = moderatelyai_sdk.ModeratelyAI(
    team_id="your-team-id",
    api_key="your-api-key"
)

# Use the client
users = client.users.list()
dataset = client.datasets.create(name="My Dataset")
agents = client.agents.list()
```

See the [Python SDK README](python/README.md) for detailed documentation.

## Development

Each SDK is self-contained in its respective directory with its own build system and dependencies.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please visit our [GitHub repository](https://github.com/moderately-ai/platform-sdk) or contact us at sdk@moderately.ai.