#!/usr/bin/env python3
"""
Async File Operations Example - Moderately AI Python SDK

This example demonstrates the complete file operations workflow using the async SDK,
showing the exact method mappings from REST API endpoints to async SDK methods.

REST API vs Async SDK Method Mapping:
- REST: POST /files/upload-url + PUT presigned-url + POST /files/{id}/complete
  SDK:  await client.files.upload(file)

- REST: GET /files/{id}/download
  SDK:  await file.download() or await client.files.download(file_id)

- REST: GET /files
  SDK:  await client.files.list()

- REST: DELETE /files/{id}
  SDK:  await file.delete() or await client.files.delete(file_id)

Usage:
    dotenvx run -- python main_async.py
"""

import asyncio
from pathlib import Path

from moderatelyai_sdk import AsyncModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError


def create_sample_file() -> Path:
    """Create a sample file for upload testing."""
    sample_content = """# Sample Data File (Async Version)
This is a test file created for demonstrating async file operations with the Moderately AI SDK.

Sample CSV Data:
name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago

This file will be uploaded, downloaded, and then deleted as part of the async example.
"""

    # Create a temporary file that we'll manage ourselves
    temp_file = Path("sample_data_async.txt")
    temp_file.write_text(sample_content)
    print(
        f"✅ Created sample file: {temp_file.name} ({temp_file.stat().st_size} bytes)"
    )
    return temp_file


async def main():
    """Demonstrate complete async file operations workflow."""
    print("🚀 Async File Operations Example - Moderately AI SDK")
    print("=" * 60)

    try:
        # Initialize the async SDK client
        # This reads MODERATELY_API_KEY and MODERATELY_TEAM_ID from environment
        print("\n1️⃣ Initializing Async SDK Client...")
        async with AsyncModeratelyAI() as client:
            print(f"✅ Async client initialized for team: {client.team_id}")

            # Create a sample file to upload
            sample_file = create_sample_file()
            uploaded_file = None

            try:
                # 2. Upload File Operation
                print("\n2️⃣ Uploading File...")
                print(f"   File: {sample_file.name}")
                print(f"   Size: {sample_file.stat().st_size} bytes")

                # Async SDK Method: await client.files.upload(file, name=None, metadata=None)
                #
                # This single async method call replaces the entire 3-step REST workflow:
                #   1. POST /files/upload-url → Get presigned S3 URL and file metadata
                #   2. PUT {presigned-url} → Upload file directly to S3 with proper headers
                #   3. POST /files/{id}/complete → Mark upload complete with hash/size verification
                #
                # Parameters:
                #   file: File path, bytes, or file-like object
                #   name: Optional display name (defaults to filename)
                #   metadata: Optional dict of custom metadata
                #
                # Returns: FileAsyncModel instance with rich async methods
                uploaded_file = await client.files.upload(
                    file=sample_file,
                    name="Async Sample Data File",
                    metadata={"category": "example", "source": "async_sdk_demo"},
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

                # Async SDK Method: await client.files.list(**filters)
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
                # Returns: Dict with "items" (list of FileAsyncModel) and "pagination" metadata
                # Note: Team filtering is automatic based on client configuration
                files_response = await client.files.list(
                    page_size=5, order_direction="desc"  # Most recent first
                )

                files = files_response["items"]
                pagination = files_response.get("pagination", {})

                total_pages = pagination.get(
                    "totalPages", pagination.get("total_pages", 1)
                )
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

                    print(
                        f"   {status_icon} {file.name}{file_type} ({file.file_size} bytes)"
                    )

                # 4. Download File Operation (Method 1: Using FileAsyncModel)
                print("\n4️⃣ Downloading File (Method 1: FileAsyncModel)...")

                # Async SDK Method: await file.download(path=None)
                #
                # This maps to: GET /files/{file_id}/download → Returns presigned S3 URL → Downloads content
                #
                # Parameters:
                #   path: Optional file path to save to disk
                #         If None: returns file content as bytes
                #         If provided: saves to path and returns None
                #
                # The async method handles:
                #   - Getting download URL from API
                #   - Following presigned S3 URL with async HTTP client
                #   - Creating parent directories if needed
                #   - Automatic binary/text handling
                download_path = Path("downloaded_sample_async.txt")
                await uploaded_file.download(path=download_path)

                print(f"✅ File downloaded to: {download_path}")
                print(f"   Size: {download_path.stat().st_size} bytes")

                # Verify content
                downloaded_content = download_path.read_text()
                original_content = sample_file.read_text()
                if downloaded_content == original_content:
                    print("✅ Content verification: Files match perfectly!")
                else:
                    print("⚠️  Content verification: Files differ")

                # 5. Download File Operation (Method 2: Using Async Client)
                print("\n5️⃣ Downloading File (Method 2: AsyncFiles Resource)...")

                # Async SDK Method: await client.files.download(file_id)
                #
                # Alternative approach using the AsyncFiles resource directly instead of FileAsyncModel
                # Same REST mapping as above but called through async resource layer
                #
                # Parameters:
                #   file_id: The ID of the file to download
                #
                # Use this when you have a file ID but no FileAsyncModel instance
                content_bytes = await client.files.download(uploaded_file.file_id)

                if content_bytes:
                    print(f"✅ File downloaded to memory: {len(content_bytes)} bytes")
                else:
                    print("✅ File downloaded to memory successfully")

                # 6. File Information and Rich Methods
                print("\n6️⃣ File Information & Rich Methods...")

                # FileAsyncModel provides rich properties and methods without additional API calls:
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

                # 7. Delete File Operation (Method 1: Using FileAsyncModel)
                print("\n7️⃣ Deleting File (Method 1: FileAsyncModel)...")

                # Async SDK Method: await file.delete()
                #
                # This maps to: DELETE /files/{file_id}
                #
                # Permanently deletes the file from both database and cloud storage
                # This operation cannot be undone
                #
                # Alternative: await client.files.delete(file_id) - same REST call, async resource-level method
                await uploaded_file.delete()
                print("✅ File deleted successfully using FileAsyncModel.delete()")

                print("\n🎉 Async file operations completed successfully!")
                print("\nSummary of Async SDK Methods Used:")
                print("  • await client.files.upload() - Complete upload workflow")
                print("  • await client.files.list() - List files with filtering")
                print("  • await file.download() - Download using FileAsyncModel")
                print(
                    "  • await client.files.download() - Download using AsyncFiles resource"
                )
                print("  • await file.delete() - Delete using FileAsyncModel")

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
                    Path("downloaded_sample_async.txt").unlink(missing_ok=True)
                    print("\n🧹 Cleaned up local files")
                except Exception as e:
                    print(f"⚠️  Warning: Could not clean up local files: {e}")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nMake sure to set environment variables:")
        print("  MODERATELY_API_KEY=your_api_key")
        print("  MODERATELY_TEAM_ID=your_team_id")
        print("\nOr run with: dotenvx run -- python main_async.py")
        return 1

    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("Please check your API key is valid")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
