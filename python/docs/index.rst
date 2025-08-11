Moderately AI Python SDK
=========================

The official Python SDK for the Moderately AI platform, providing programmatic access to agents, datasets, pipelines, and team management.

.. image:: https://img.shields.io/pypi/v/moderatelyai-sdk.svg
    :target: https://pypi.org/project/moderatelyai-sdk/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/moderatelyai-sdk.svg
    :target: https://pypi.org/project/moderatelyai-sdk/
    :alt: Python Versions

.. image:: https://img.shields.io/github/license/moderately-ai/platform-sdk.svg
    :target: https://github.com/moderately-ai/platform-sdk/blob/main/LICENSE
    :alt: License

Features
--------

- **Python 3.8+ Support**: Compatible with Python 3.8 and later versions
- **Type Safety**: Full type annotations with mypy support
- **Async/Await**: Built-in support for asynchronous operations
- **Team-scoped Operations**: Automatic filtering and scoping to your team
- **Resource Management**: Agents, datasets, pipelines, files, and users
- **Error Handling**: Comprehensive exception handling for different error scenarios
- **Rate Limiting**: Built-in rate limit handling and retry logic

Quick Start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

    pip install moderatelyai-sdk

Basic Usage
^^^^^^^^^^^

**Synchronous Client**

.. code-block:: python

    import moderatelyai_sdk

    # Initialize with environment variables (recommended)
    client = moderatelyai_sdk.ModeratelyAI()

    # Use the client - all operations are automatically scoped to your team
    users = client.users.list()
    dataset = client.datasets.create(name="My Dataset")
    agents = client.agents.list()

**Asynchronous Client**

.. code-block:: python

    import asyncio
    import moderatelyai_sdk

    async def main():
        async with moderatelyai_sdk.AsyncModeratelyAI() as client:
            users = await client.users.list()
            dataset = await client.datasets.create(name="My Dataset")
            agents = await client.agents.list()

    asyncio.run(main())

Examples
--------

Complete working examples are available in the `examples directory <https://github.com/moderately-ai/platform-sdk/tree/main/python/examples>`_:

- **File Operations** - Complete file upload, download, and management workflows
  
  - Synchronous and asynchronous examples
  - REST API to SDK method mappings  
  - Error handling and cleanup patterns

User Guide
----------

.. toctree::
   :maxdepth: 2

   user_guide/installation
   user_guide/quickstart
   user_guide/authentication
   user_guide/file_operations
   user_guide/datasets
   user_guide/agents
   user_guide/pipelines
   user_guide/async_usage
   user_guide/error_handling
   user_guide/configuration

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/clients
   api/resources
   api/models
   api/exceptions
   api/types

Development
-----------

.. toctree::
   :maxdepth: 2

   development/contributing
   development/testing
   development/release_process

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`