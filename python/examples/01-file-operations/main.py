#!/usr/bin/env python3
"""
File Operations Example - Moderately AI Python SDK

This example demonstrates the complete file operations workflow using the SDK,
showing the exact method mappings from REST API endpoints to SDK methods.

REST API vs SDK Method Mapping:
- REST: POST /files/upload-url + PUT presigned-url + POST /files/{id}/complete
  SDK:  client.files.upload(file_path)

- REST: GET /files/{id}/download
  SDK:  file.download() or client.files.download(file_id)

- REST: GET /files
  SDK:  client.files.list()

- REST: DELETE /files/{id}
  SDK:  file.delete() or client.files.delete(file_id)

Usage:
    dotenvx run -- python main.py
"""

from pathlib import Path

from moderatelyai_sdk import ModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError


def create_sample_file() -> Path:
    """Create a sample file for upload testing."""
    sample_content = """# Sample Data File
This is a test file created for demonstrating file operations with the Moderately AI SDK.

Sample CSV Data:
name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago

This file will be uploaded, downloaded, and then deleted as part of the example.
"""

    # Create a temporary file that we'll manage ourselves
    temp_file = Path("sample_data.txt")
    temp_file.write_text(sample_content)
    print(
        f"✅ Created sample file: {temp_file.name} ({temp_file.stat().st_size} bytes)"
    )
    return temp_file


def main():
    """Demonstrate complete file operations workflow."""
    print("🚀 File Operations Example - Moderately AI SDK")
    print("=" * 60)

    try:
        # Initialize the SDK client
        # This reads MODERATELY_API_KEY and MODERATELY_TEAM_ID from environment
        print("\n1️⃣ Initializing SDK Client...")
        client = ModeratelyAI()
        print(f"✅ Client initialized for team: {client.team_id}")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nMake sure to set environment variables:")
        print("  MODERATELY_API_KEY=your_api_key")
        print("  MODERATELY_TEAM_ID=your_team_id")
        print("\nOr run with: dotenvx run -- python main.py")
        return 1

    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("Please check your API key is valid")
        return 1

    # Create a sample file to upload
    sample_file = create_sample_file()
    uploaded_file = None

    try:
        # 2. Upload File Operation
        print("\n2️⃣ Uploading File...")
        print(f"   File: {sample_file.name}")
        print(f"   Size: {sample_file.stat().st_size} bytes")

        # SDK Method: client.files.upload(file, name=None, metadata=None)
        #
        # This single method call replaces the entire 3-step REST workflow:
        #   1. POST /files/upload-url → Get presigned S3 URL and file metadata
        #   2. PUT {presigned-url} → Upload file directly to S3 with proper headers
        #   3. POST /files/{id}/complete → Mark upload complete with hash/size verification
        #
        # Parameters:
        #   file: File path, bytes, or file-like object
        #   name: Optional display name (defaults to filename)
        #   metadata: Optional dict of custom metadata
        #
        # Returns: FileModel instance with rich methods
        uploaded_file = client.files.upload(
            file=sample_file,
            name="Sample Data File",
            metadata={"category": "example", "source": "sdk_demo"},
        )

        print("✅ File uploaded successfully!")
        print(f"   File ID: {uploaded_file.file_id}")
        print(f"   Name: {uploaded_file.name}")
        print(f"   Size: {uploaded_file.file_size} bytes")
        print(f"   MIME Type: {uploaded_file.mime_type}")
        print(f"   Status: {uploaded_file.status}")
        print(f"   Is Ready: {uploaded_file.is_ready()}")

        # 3. List Files Operation
        print("\n3️⃣ Listing Files...")

        # SDK Method: client.files.list(**filters)
        #
        # This maps to: GET /files?teamIds={team_id}&page=1&pageSize=10&...
        #
        # Parameters:
        #   dataset_id: Filter by dataset ID
        #   status: Filter by status ("completed", "processing", "error")
        #   mime_type: Filter by MIME type ("text/csv", "application/pdf")
        #   page: Page number (1-based)
        #   page_size: Items per page (max 100)
        #   order_by: Sort field ("created_at", "file_size", "name")
        #   order_direction: "asc" or "desc"
        #
        # Returns: Dict with "items" (list of FileModel) and "pagination" metadata
        # Note: Team filtering is automatic based on client configuration
        files_response = client.files.list(
            page_size=5, order_direction="desc"  # Most recent first
        )

        files = files_response["items"]
        pagination = files_response.get("pagination", {})

        total_pages = pagination.get("totalPages", pagination.get("total_pages", 1))
        print(f"✅ Found {len(files)} files (page 1 of {total_pages}):")
        for file in files[:3]:  # Show first 3
            status_icon = "✅" if file.is_ready() else "⏳"
            file_type = ""
            if file.is_csv():
                file_type = " [CSV]"
            elif file.is_document():
                file_type = " [DOC]"
            elif file.is_image():
                file_type = " [IMG]"

            print(f"   {status_icon} {file.name}{file_type} ({file.file_size} bytes)")

        # 4. Download File Operation (Method 1: Using FileModel)
        print("\n4️⃣ Downloading File (Method 1: FileModel)...")

        # SDK Method: file.download(path=None)
        #
        # This maps to: GET /files/{file_id}/download → Returns presigned S3 URL → Downloads content
        #
        # Parameters:
        #   path: Optional file path to save to disk
        #         If None: returns file content as bytes
        #         If provided: saves to path and returns None
        #
        # The method handles:
        #   - Getting download URL from API
        #   - Following presigned S3 URL
        #   - Creating parent directories if needed
        #   - Automatic binary/text handling
        download_path = Path("downloaded_sample.txt")
        uploaded_file.download(path=download_path)

        print(f"✅ File downloaded to: {download_path}")
        print(f"   Size: {download_path.stat().st_size} bytes")

        # Verify content
        downloaded_content = download_path.read_text()
        original_content = sample_file.read_text()
        if downloaded_content == original_content:
            print("✅ Content verification: Files match perfectly!")
        else:
            print("⚠️  Content verification: Files differ")

        # 5. Download File Operation (Method 2: Using Client)
        print("\n5️⃣ Downloading File (Method 2: Client Resource)...")

        # SDK Method: client.files.download(file_id, path=None)
        #
        # Alternative approach using the Files resource directly instead of FileModel
        # Same REST mapping as above but called through resource layer
        #
        # Parameters:
        #   file_id: The ID of the file to download
        #   path: Optional file path (same behavior as FileModel.download)
        #
        # Use this when you have a file ID but no FileModel instance
        content_bytes = client.files.download(uploaded_file.file_id)

        if content_bytes:
            print(f"✅ File downloaded to memory: {len(content_bytes)} bytes")
        else:
            print("✅ File downloaded to memory successfully")

        # 6. File Information and Rich Methods
        print("\n6️⃣ File Information & Rich Methods...")

        # FileModel provides rich properties and methods without additional API calls:
        # Properties: file_id, name, file_size, mime_type, status, created_at, etc.
        # Type detection: is_csv(), is_document(), is_image(), is_text()
        # Status checking: is_ready(), is_processing(), has_error()
        # Utilities: get_extension()
        print(f"   Extension: {uploaded_file.get_extension()}")
        print(f"   Is Text: {uploaded_file.is_text()}")
        print(f"   Is CSV: {uploaded_file.is_csv()}")
        print(f"   Is Document: {uploaded_file.is_document()}")
        print(f"   Is Image: {uploaded_file.is_image()}")
        print(f"   Is Ready: {uploaded_file.is_ready()}")
        print(f"   Is Processing: {uploaded_file.is_processing()}")
        print(f"   Has Error: {uploaded_file.has_error()}")

        # 7. Delete File Operation (Method 1: Using FileModel)
        print("\n7️⃣ Deleting File (Method 1: FileModel)...")

        # SDK Method: file.delete()
        #
        # This maps to: DELETE /files/{file_id}
        #
        # Permanently deletes the file from both database and cloud storage
        # This operation cannot be undone
        #
        # Alternative: client.files.delete(file_id) - same REST call, resource-level method
        uploaded_file.delete()
        print("✅ File deleted successfully using FileModel.delete()")

        print("\n🎉 File operations completed successfully!")
        print("\nSummary of SDK Methods Used:")
        print("  • client.files.upload() - Complete upload workflow")
        print("  • client.files.list() - List files with filtering")
        print("  • file.download() - Download using FileModel")
        print("  • client.files.download() - Download using resource")
        print("  • file.delete() - Delete using FileModel")

    except APIError as e:
        print(f"❌ API Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1

    finally:
        # Clean up local files
        try:
            sample_file.unlink(missing_ok=True)
            Path("downloaded_sample.txt").unlink(missing_ok=True)
            print("\n🧹 Cleaned up local files")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up local files: {e}")

    return 0


if __name__ == "__main__":
    exit(main())
