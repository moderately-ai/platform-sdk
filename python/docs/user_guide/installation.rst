Installation
============

Requirements
------------

- Python 3.8 or higher
- pip package manager

Install from PyPI
------------------

The easiest way to install the Moderately AI Python SDK is using pip:

.. code-block:: bash

    pip install moderatelyai-sdk

This will install the latest stable version from PyPI along with all required dependencies.

Install from Source
-------------------

To install the latest development version from GitHub:

.. code-block:: bash

    git clone https://github.com/moderately-ai/platform-sdk.git
    cd platform-sdk/python
    pip install -e .

Development Installation
------------------------

For development, it's recommended to use PDM:

.. code-block:: bash

    # Install PDM
    pip install pdm

    # Clone repository
    git clone https://github.com/moderately-ai/platform-sdk.git
    cd platform-sdk/python

    # Install dependencies
    pdm install

    # Install pre-commit hooks
    pdm run pre-commit install

Dependencies
------------

The SDK has minimal dependencies:

- ``httpx`` (>=0.24.0) - Modern HTTP client for API requests
- ``pydantic`` (>=1.10.0) - Data validation and parsing
- ``typing-extensions`` (>=4.0.0) - Backport of Python typing features
- ``aiofiles`` (>=23.0.0) - Async file I/O operations

Verification
------------

To verify your installation:

.. code-block:: python

    import moderatelyai_sdk
    print(moderatelyai_sdk.__version__)

Optional Dependencies
---------------------

For development and testing:

.. code-block:: bash

    pip install moderatelyai-sdk[dev]

This includes:

- ``pytest`` - Testing framework
- ``mypy`` - Type checking
- ``ruff`` - Linting and formatting
- ``pre-commit`` - Git hooks for code quality