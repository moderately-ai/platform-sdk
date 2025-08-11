Quick Start
===========

This guide will get you up and running with the Moderately AI Python SDK in minutes.

Setup
-----

First, install the SDK:

.. code-block:: bash

    pip install moderatelyai-sdk

Get your API credentials from the Moderately AI platform:

- **API Key**: Your authentication token
- **Team ID**: Your team identifier

Environment Variables
----------------------

Set your credentials as environment variables (recommended):

.. code-block:: bash

    export MODERATELY_API_KEY="your-api-key-here"
    export MODERATELY_TEAM_ID="your-team-id-here"

Or create a ``.env`` file:

.. code-block:: bash

    MODERATELY_API_KEY=your-api-key-here
    MODERATELY_TEAM_ID=your-team-id-here

Basic Usage
-----------

Synchronous Client
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import moderatelyai_sdk

    # Initialize client with environment variables
    client = moderatelyai_sdk.ModeratelyAI()

    # Or initialize with explicit credentials
    client = moderatelyai_sdk.ModeratelyAI(
        team_id="your-team-id",
        api_key="your-api-key"
    )

    # List users in your team
    users = client.users.list()
    print(f"Found {len(users)} users")

    # Create a dataset
    dataset = client.datasets.create(
        name="My First Dataset",
        description="A test dataset"
    )

    # Upload a file
    file = client.files.upload(
        file="path/to/your/file.csv",
        name="Training Data"
    )

Asynchronous Client
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    import moderatelyai_sdk

    async def main():
        # Use async context manager (recommended)
        async with moderatelyai_sdk.AsyncModeratelyAI() as client:
            # Same operations, just with await
            users = await client.users.list()
            print(f"Found {len(users)} users")

            dataset = await client.datasets.create(
                name="My Async Dataset",
                description="A test dataset created asynchronously"
            )

            file = await client.files.upload(
                file="path/to/your/file.csv",
                name="Async Training Data"
            )

    # Run the async function
    asyncio.run(main())

Working with Files
------------------

Files are one of the most common resources you'll work with:

.. code-block:: python

    # Upload a file
    file = client.files.upload(
        file="/path/to/document.pdf",
        name="Important Document",
        metadata={"category": "legal", "priority": "high"}
    )

    # Check file status
    if file.is_ready():
        print(f"File ready: {file.name} ({file.file_size} bytes)")
        
        # Download file content
        content = file.download()  # To memory
        file.download(path="./local_copy.pdf")  # To disk
        
        # Check file type
        if file.is_document():
            print("This is a document file")
        elif file.is_csv():
            print("This is a CSV file")

    # Clean up
    file.delete()

Error Handling
--------------

Always handle errors appropriately:

.. code-block:: python

    from moderatelyai_sdk import (
        ModeratelyAI, 
        APIError, 
        AuthenticationError,
        NotFoundError
    )

    client = ModeratelyAI()

    try:
        dataset = client.datasets.create(name="Test Dataset")
        print(f"Created dataset: {dataset['datasetId']}")
    except AuthenticationError:
        print("Invalid API key or insufficient permissions")
    except APIError as e:
        print(f"API error occurred: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")

Next Steps
----------

- Learn about :doc:`file_operations` for detailed file handling
- Explore :doc:`datasets` for data management
- Check out :doc:`agents` for AI agent integration  
- See :doc:`async_usage` for async patterns
- Review the complete :doc:`../api/clients` API reference

For complete examples, visit the `examples directory <https://github.com/moderately-ai/platform-sdk/tree/main/python/examples>`_ in the repository.