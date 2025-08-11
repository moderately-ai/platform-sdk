File Operations
===============

The SDK provides comprehensive file management capabilities with automatic presigned URL handling, rich file models, and support for various file operations.

Upload Files
------------

Basic Upload
^^^^^^^^^^^^

.. code-block:: python

    from moderatelyai_sdk import ModeratelyAI

    client = ModeratelyAI()

    # Upload from file path
    file = client.files.upload(
        file="/path/to/document.pdf",
        name="Important Document"
    )

    print(f"Uploaded: {file.name} ({file.file_size} bytes)")

Upload with Metadata
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Upload with custom metadata
    file = client.files.upload(
        file="data.csv",
        name="Training Dataset",
        metadata={
            "category": "machine-learning",
            "version": "1.0",
            "source": "production"
        }
    )

Multiple Input Types
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # From file path (string)
    file1 = client.files.upload(
        file="/path/to/file.pdf",
        name="Document"
    )

    # From pathlib.Path
    from pathlib import Path
    file2 = client.files.upload(
        file=Path("data.csv"),
        name="Dataset"
    )

    # From bytes
    with open("image.png", "rb") as f:
        file3 = client.files.upload(
            file=f.read(),
            name="Profile Picture"
        )

    # From file object
    with open("document.docx", "rb") as f:
        file4 = client.files.upload(
            file=f,
            name="Report"
        )

List Files
----------

Basic Listing
^^^^^^^^^^^^^

.. code-block:: python

    # List all files
    files_response = client.files.list()
    files = files_response["items"]

    for file in files:
        print(f"File: {file.name} ({file.file_size} bytes)")

Filtered Listing
^^^^^^^^^^^^^^^^

.. code-block:: python

    # Filter by MIME type
    pdf_files = client.files.list(mime_type="application/pdf")

    # Pagination
    first_page = client.files.list(page_size=10)
    
    # Ordering
    recent_files = client.files.list(
        order_direction="desc",
        page_size=20
    )

File Properties
---------------

Rich File Model
^^^^^^^^^^^^^^^

.. code-block:: python

    file = client.files.retrieve("file_123")

    # Basic properties
    print(f"ID: {file.file_id}")
    print(f"Name: {file.name}")
    print(f"Original name: {file.original_name}")
    print(f"Size: {file.file_size} bytes")
    print(f"MIME type: {file.mime_type}")
    print(f"Extension: {file.get_extension()}")

    # Status checks
    if file.is_ready():
        print("File is ready for use")
    elif file.is_processing():
        print("File is still processing")
    elif file.has_error():
        print("File processing failed")

Type Detection
^^^^^^^^^^^^^^

.. code-block:: python

    # Check file types
    if file.is_image():
        print("Image file")
    elif file.is_document():
        print("Document file (PDF, Word, etc.)")
    elif file.is_csv():
        print("CSV file")
    elif file.is_text():
        print("Text file")

    # Get file extension
    extension = file.get_extension()
    if extension == '.pdf':
        print("PDF document")

Download Files
--------------

Download to Memory
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    file = client.files.retrieve("file_123")

    # Download to memory as bytes
    content = file.download()
    
    # For text files, decode to string
    if file.is_text():
        text_content = content.decode('utf-8')
        print(text_content[:100])  # First 100 characters

Download to Disk
^^^^^^^^^^^^^^^^

.. code-block:: python

    # Download to specific path
    file.download(path="./downloads/document.pdf")

    # Download with automatic directory creation
    file.download(path="./new_folder/subfolder/file.csv")
    # Creates ./new_folder/subfolder/ if it doesn't exist

    # Download with original filename
    original_path = f"./downloads/{file.original_name}"
    file.download(path=original_path)

Error Handling
^^^^^^^^^^^^^^

.. code-block:: python

    from moderatelyai_sdk import APIError

    try:
        content = file.download()
    except APIError as e:
        if "not ready" in str(e):
            print("File is not ready for download yet")
        else:
            print(f"Download failed: {e}")

Delete Files
------------

Basic Deletion
^^^^^^^^^^^^^^

.. code-block:: python

    # Delete using file model
    file = client.files.retrieve("file_123")
    file.delete()

    # Or delete directly by ID
    client.files.delete("file_123")

Bulk Operations
^^^^^^^^^^^^^^^

.. code-block:: python

    # Delete multiple files
    files = client.files.list()["items"]
    
    for file in files:
        if file.name.startswith("temp_"):
            print(f"Deleting {file.name}")
            file.delete()

Asynchronous File Operations
----------------------------

All file operations work identically with the async client:

Basic Async Usage
^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    from moderatelyai_sdk import AsyncModeratelyAI

    async def file_operations():
        async with AsyncModeratelyAI() as client:
            # Upload
            file = await client.files.upload(
                file="document.pdf",
                name="Async Upload"
            )
            
            # Check status
            if file.is_ready() and file.is_document():
                # Download
                content = await file.download()
                await file.download(path="./copy.pdf")
                
                # Delete
                await file.delete()

    asyncio.run(file_operations())

Async File Processing
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    import aiofiles
    from pathlib import Path

    async def process_files_async(file_paths):
        async with AsyncModeratelyAI() as client:
            tasks = []
            
            # Upload files concurrently
            for path in file_paths:
                task = client.files.upload(
                    file=path,
                    name=Path(path).name
                )
                tasks.append(task)
            
            # Wait for all uploads
            files = await asyncio.gather(*tasks)
            
            # Process ready files
            for file in files:
                if file.is_ready():
                    content = await file.download()
                    # Process content...

Complete Example
----------------

File Operations Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from moderatelyai_sdk import ModeratelyAI, APIError
    from pathlib import Path
    import time

    def complete_file_workflow():
        client = ModeratelyAI()
        
        try:
            # 1. Upload a file
            print("Uploading file...")
            file = client.files.upload(
                file="./data/dataset.csv",
                name="Training Dataset",
                metadata={
                    "project": "ml-experiment-1",
                    "stage": "training"
                }
            )
            
            print(f"✓ Uploaded: {file.file_id}")
            print(f"  Name: {file.name}")
            print(f"  Size: {file.file_size} bytes")
            print(f"  Type: {file.mime_type}")
            
            # 2. Wait for processing (if needed)
            while file.is_processing():
                print("  Processing...")
                time.sleep(2)
                file._refresh()  # Refresh status
            
            if file.has_error():
                print("✗ File processing failed")
                return
            
            # 3. Work with the file
            print("✓ File is ready")
            
            if file.is_csv():
                print("  This is a CSV file - good for datasets")
            
            # 4. Download for verification
            print("Downloading file...")
            content = file.download()
            print(f"✓ Downloaded {len(content)} bytes")
            
            # Also save a local copy
            file.download(path="./downloads/backup.csv")
            print("✓ Saved backup copy")
            
            # 5. List files to see our upload
            print("Current files:")
            files = client.files.list(page_size=5)["items"]
            for f in files:
                status_emoji = "✓" if f.is_ready() else "⏳" if f.is_processing() else "✗"
                print(f"  {status_emoji} {f.name} ({f.file_size} bytes)")
            
            # 6. Clean up (optional)
            # file.delete()
            # print("✓ File deleted")
            
        except APIError as e:
            print(f"✗ API Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")

    if __name__ == "__main__":
        complete_file_workflow()

For complete working examples, see the `file operations examples <https://github.com/moderately-ai/platform-sdk/tree/main/python/examples/01-file-operations>`_ in the repository.