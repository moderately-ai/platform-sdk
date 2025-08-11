Authentication
==============

The Moderately AI SDK uses API key authentication to access the platform securely.

API Key Setup
-------------

Obtain Your Credentials
^^^^^^^^^^^^^^^^^^^^^^^^

1. Log in to the Moderately AI platform
2. Navigate to your team settings
3. Generate or copy your API key
4. Note your team ID

Environment Variables (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set your credentials as environment variables:

.. code-block:: bash

    export MODERATELY_API_KEY="your-api-key-here"
    export MODERATELY_TEAM_ID="your-team-id-here"

Using a ``.env`` file:

.. code-block:: bash

    # .env file
    MODERATELY_API_KEY=your-api-key-here
    MODERATELY_TEAM_ID=your-team-id-here

Then load with dotenvx:

.. code-block:: bash

    dotenvx run -- python your_script.py

Client Configuration
--------------------

Automatic Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The SDK automatically reads environment variables:

.. code-block:: python

    import moderatelyai_sdk

    # Reads MODERATELY_API_KEY and MODERATELY_TEAM_ID
    client = moderatelyai_sdk.ModeratelyAI()

    # For async client
    async with moderatelyai_sdk.AsyncModeratelyAI() as client:
        pass

Explicit Configuration
^^^^^^^^^^^^^^^^^^^^^^

Pass credentials directly:

.. code-block:: python

    client = moderatelyai_sdk.ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id"
    )

    # For async client
    async with moderatelyai_sdk.AsyncModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id"
    ) as client:
        pass

Advanced Configuration
----------------------

Custom Base URL
^^^^^^^^^^^^^^^

For different environments or self-hosted instances:

.. code-block:: python

    client = moderatelyai_sdk.ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id",
        base_url="https://custom-api.example.com"
    )

Timeout Configuration
^^^^^^^^^^^^^^^^^^^^^

Configure request timeouts:

.. code-block:: python

    client = moderatelyai_sdk.ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id",
        timeout=60  # 60 seconds timeout
    )

    # Or with detailed timeout configuration
    import httpx
    
    timeout = httpx.Timeout(
        connect=10.0,  # 10 seconds to connect
        read=30.0,     # 30 seconds to read response
        write=10.0,    # 10 seconds to send request
        pool=5.0       # 5 seconds to get connection from pool
    )
    
    client = moderatelyai_sdk.ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id",
        timeout=timeout
    )

Retry Configuration
^^^^^^^^^^^^^^^^^^^

Configure retry behavior:

.. code-block:: python

    from moderatelyai_sdk import ModeratelyAI, RetryConfig

    retry_config = RetryConfig(
        max_retries=5,
        backoff_factor=2.0,
        max_backoff=60.0,
        retryable_status_codes=[429, 502, 503, 504]
    )

    client = ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id",
        retry_config=retry_config
    )

Custom HTTP Client
^^^^^^^^^^^^^^^^^^

Use your own HTTP client instance:

.. code-block:: python

    import httpx

    http_client = httpx.Client(
        timeout=30,
        limits=httpx.Limits(max_connections=100)
    )

    client = moderatelyai_sdk.ModeratelyAI(
        api_key="your-api-key",
        team_id="your-team-id",
        http_client=http_client
    )

Error Handling
--------------

Authentication Errors
^^^^^^^^^^^^^^^^^^^^^^

Handle authentication-related errors:

.. code-block:: python

    from moderatelyai_sdk import ModeratelyAI, AuthenticationError

    try:
        client = ModeratelyAI(
            api_key="invalid-key",
            team_id="your-team-id"
        )
        users = client.users.list()
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle invalid credentials

Security Best Practices
------------------------

1. **Never hardcode credentials** in your source code
2. **Use environment variables** for credential management
3. **Rotate API keys regularly** in production
4. **Use different keys** for different environments (dev, staging, prod)
5. **Limit API key scope** if supported by the platform
6. **Store credentials securely** using secret management systems in production

Example Production Setup
------------------------

For production applications:

.. code-block:: python

    import os
    from moderatelyai_sdk import ModeratelyAI, AuthenticationError

    def create_client():
        """Create authenticated client with error handling."""
        api_key = os.getenv("MODERATELY_API_KEY")
        team_id = os.getenv("MODERATELY_TEAM_ID")
        
        if not api_key or not team_id:
            raise ValueError(
                "MODERATELY_API_KEY and MODERATELY_TEAM_ID must be set"
            )
        
        try:
            return ModeratelyAI(
                api_key=api_key,
                team_id=team_id,
                timeout=30,
                max_retries=3
            )
        except AuthenticationError:
            raise AuthenticationError(
                "Invalid credentials. Check your API key and team ID."
            )

    # Usage
    client = create_client()
    users = client.users.list()