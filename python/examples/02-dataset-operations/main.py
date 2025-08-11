#!/usr/bin/env python3
"""
Dataset Operations Example - Moderately AI Python SDK

This example demonstrates the complete dataset operations workflow using the SDK,
showing the exact method mappings from REST API endpoints to SDK methods.

REST API vs SDK Method Mapping:
- REST: POST /datasets
  SDK:  client.datasets.create(name="Dataset Name")

- REST: POST /datasets/{id}/data-versions + File Upload Flow
  SDK:  dataset.upload_data("/path/to/data.csv") 

- REST: GET /datasets/{id}/data-versions/{version_id}/download
  SDK:  dataset.download_data() or data_version.download()

- REST: POST /datasets/{id}/schema-versions  
  SDK:  dataset.create_schema([columns]) or dataset.create_schema_from_sample()

- REST: GET /datasets
  SDK:  client.datasets.list()

- REST: DELETE /datasets/{id}
  SDK:  dataset.delete() or client.datasets.delete(dataset_id)

Usage:
    python main.py
"""

import csv
from pathlib import Path

from moderatelyai_sdk import ModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError


def create_sample_csv() -> Path:
    """Create a sample CSV file for dataset testing."""
    sample_data = [
        ["customer_id", "name", "email", "signup_date", "total_orders", "is_active"],
        ["1001", "Alice Johnson", "alice@example.com", "2023-01-15", "12", "true"],
        ["1002", "Bob Smith", "bob@example.com", "2023-02-20", "8", "true"],  
        ["1003", "Charlie Brown", "charlie@example.com", "2023-03-10", "15", "false"],
        ["1004", "Diana Prince", "diana@example.com", "2023-04-05", "3", "true"],
        ["1005", "Edward Norton", "edward@example.com", "2023-05-12", "22", "true"],
    ]

    # Create CSV file
    temp_file = Path("sample_customers.csv")
    with temp_file.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sample_data)

    print(f"✅ Created sample CSV: {temp_file.name} ({temp_file.stat().st_size} bytes)")
    return temp_file




def main():
    """Demonstrate complete dataset operations workflow."""
    print("🚀 Dataset Operations Example - Moderately AI SDK")
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
        return 1

    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("Please check your API key is valid")
        return 1

    # Create sample file for testing
    csv_file = create_sample_csv()
    created_dataset = None

    try:
        # 2. Create Dataset Operation
        print("\n2️⃣ Creating Dataset...")
        
        # SDK Method: client.datasets.create(name, description=None, **kwargs)
        #
        # This maps to: POST /datasets
        # {
        #   "name": "Customer Dataset",
        #   "description": "Customer data for analysis",
        #   "teamId": "{client.team_id}"
        # }
        #
        # Parameters:
        #   name: Required dataset name
        #   description: Optional description
        #   **kwargs: Additional dataset properties
        #
        # Returns: DatasetModel instance with rich methods
        import time
        timestamp = int(time.time())
        created_dataset = client.datasets.create(
            name=f"Customer Analytics Dataset {timestamp}",
            description="Sample customer data for SDK demonstration"
        )

        print("✅ Dataset created successfully!")
        print(f"   Dataset ID: {created_dataset.dataset_id}")
        print(f"   Name: {created_dataset.name}")
        print(f"   Description: {created_dataset.description}")
        print(f"   Team ID: {created_dataset.team_id}")
        print(f"   Status: {created_dataset.processing_status}")
        print(f"   Record Count: {created_dataset.record_count}")

        # 3. Upload Data Operation (CSV)
        print("\n3️⃣ Uploading CSV Data...")
        print(f"   File: {csv_file.name}")
        print(f"   Size: {csv_file.stat().st_size} bytes")

        # SDK Method: dataset.upload_data(file, file_type=None, status="current", **kwargs)
        #
        # This replaces the complex REST workflow:
        #   1. POST /datasets/{id}/data-versions → Create version record
        #   2. POST /files/upload-url → Get presigned S3 URL  
        #   3. PUT {presigned-url} → Upload file to S3
        #   4. POST /files/{file_id}/complete → Mark upload complete
        #   5. PATCH /datasets/{id}/data-versions/{version_id} → Link file to version
        #
        # Parameters:
        #   file: File path, bytes, or file-like object
        #   file_type: "csv" or "xlsx" (auto-detected if not provided)
        #   status: "current" or "draft" (defaults to "current")
        #   **kwargs: Additional version metadata
        #
        # Returns: DatasetDataVersionModel instance
        data_version = created_dataset.upload_data(
            file=csv_file,
            file_type="csv",  # Auto-detected from extension
            status="current"
        )

        print("✅ CSV data uploaded successfully!")
        print(f"   Version ID: {data_version.dataset_data_version_id}")
        print(f"   Version Number: {data_version.version_no}")
        print(f"   Row Count: {data_version.row_count}")
        print(f"   File Type: {data_version.file_type}")
        print(f"   Status: {data_version.status}")

        # 4. Create Schema from Sample Data
        print("\n4️⃣ Creating Schema from Sample...")

        # SDK Method: dataset.create_schema_from_sample(sample_file, status="draft", header_row=1, sample_size=100)
        #
        # This maps to: POST /datasets/{id}/schema-versions with auto-inferred schema
        # The method:
        #   1. Reads the sample file (CSV supported)
        #   2. Analyzes headers and sample data  
        #   3. Infers column types (string, int, float, boolean, datetime)
        #   4. Creates schema with inferred definitions
        #
        # Parameters:
        #   sample_file: Path to file for schema inference
        #   status: "draft" or "current" (defaults to "draft")  
        #   header_row: Which row contains headers (1-based, defaults to 1)
        #   sample_size: Number of rows to sample (defaults to 100)
        #
        # Returns: DatasetSchemaVersionModel instance
        schema_version = created_dataset.create_schema_from_sample(
            sample_file=csv_file,
            status="draft",
            header_row=1,
            sample_size=50
        )

        print("✅ Schema created from sample data!")
        print(f"   Schema ID: {schema_version.dataset_schema_version_id}")
        print(f"   Columns: {len(schema_version.columns)}")
        print(f"   Status: {schema_version.status}")

        # Show inferred schema
        columns = schema_version.columns
        print("   Inferred Schema:")
        for col in columns[:3]:  # Show first 3 columns
            col_type = col.get("type", "unknown")
            required = " (required)" if not col.get("nullable", True) else ""
            print(f"     • {col['name']}: {col_type}{required}")
        if len(columns) > 3:
            print(f"     ... and {len(columns) - 3} more columns")

        # 5. Create Manual Schema Operation  
        print("\n5️⃣ Creating Manual Schema...")

        # SDK Method: dataset.create_schema(columns, status="draft", parsing_options=None)
        #
        # This maps to: POST /datasets/{id}/schema-versions
        #
        # Parameters:
        #   columns: List of column definitions with name, type, required, description
        #   status: "draft" or "current" (defaults to "draft")
        #   parsing_options: Optional parsing configuration (delimiter, header_row, etc.)
        #
        # Column Definition Format:
        #   {
        #     "name": "column_name",
        #     "type": "string|int|float|boolean|datetime|date|time", 
        #     "required": true/false,
        #     "description": "Optional description"
        #   }
        #
        # Returns: DatasetSchemaVersionModel instance
        manual_schema_columns = [
            {"name": "customer_id", "type": "int", "required": True, "description": "Unique customer identifier"},
            {"name": "name", "type": "string", "required": True, "description": "Customer full name"},
            {"name": "email", "type": "string", "required": True, "description": "Customer email address"},
            {"name": "signup_date", "type": "date", "required": True, "description": "Date customer signed up"},
            {"name": "total_orders", "type": "int", "required": False, "description": "Total number of orders"},
            {"name": "is_active", "type": "boolean", "required": False, "description": "Whether customer is active"},
        ]

        manual_schema = created_dataset.create_schema(
            columns=manual_schema_columns,
            status="current",  # Make this the current schema
            parsing_options={
                "delimiter": ",",
                "headerRow": 1,  # API expects camelCase
                "encoding": "utf-8"
            }
        )

        print("✅ Manual schema created successfully!")
        print(f"   Schema ID: {manual_schema.dataset_schema_version_id}")
        print(f"   Status: {manual_schema.status}")
        print(f"   Columns: {len(manual_schema.columns)}")

        # 6. List Datasets Operation
        print("\n6️⃣ Listing Datasets...")

        # SDK Method: client.datasets.list(**filters)
        #
        # This maps to: GET /datasets?teamIds={team_id}&page=1&pageSize=10&...
        #
        # Parameters:
        #   dataset_ids: Filter by specific dataset IDs  
        #   name_like: Filter by datasets with names containing text
        #   name: Filter by exact dataset name
        #   page: Page number (1-based, defaults to 1)
        #   page_size: Items per page (defaults to 10)
        #   order_by: Sort field ("createdAt", "updatedAt", "name", defaults to "createdAt")
        #   order_direction: "asc" or "desc" (defaults to "desc")
        #
        # Returns: Dict with "items" (list of DatasetModel) and "pagination" metadata
        # Note: Team filtering is automatic based on client configuration
        datasets_response = client.datasets.list(
            page_size=5,
            order_direction="desc",  # Most recent first
            name_like="Customer"     # Filter by name containing "Customer"
        )

        datasets = datasets_response["items"]
        pagination = datasets_response.get("pagination", {})

        total_pages = pagination.get("totalPages", pagination.get("total_pages", 1))
        print(f"✅ Found {len(datasets)} datasets (page 1 of {total_pages}):")
        for dataset in datasets[:3]:  # Show first 3
            # Fix status icon logic to handle different processing states
            if dataset.processing_status == "completed":
                status_icon = "✅"
            elif dataset.processing_status in ["processing", "needs-processing"]:
                status_icon = "⏳"
            elif dataset.processing_status == "error":
                status_icon = "❌"
            else:
                status_icon = "📋"  # Default for unknown/new states
            
            record_info = f" ({dataset.record_count} records)" if dataset.record_count else ""
            print(f"   {status_icon} {dataset.name}{record_info}")
            # Note: Processing status may be None in listings but gets populated when individually fetched

        # 7. Download Data Operation (Method 1: Current Data)
        print("\n7️⃣ Downloading Current Dataset Data...")

        # SDK Method: dataset.download_data(version_id=None, path=None)
        #
        # This maps to: GET /datasets/{id}/data-versions/{version_id}/download → Returns presigned URL → Downloads content
        #
        # Note: After uploading data, we need to refetch the dataset to get updated currentDataVersionId
        print("   Refetching dataset to get current data version...")
        created_dataset = client.datasets.retrieve(created_dataset.dataset_id)
        print(f"   Current Data Version ID: {created_dataset.current_data_version_id}")

        # Parameters:
        #   version_id: Optional specific version ID (uses current if not provided)
        #   path: Optional file path to save to disk
        #         If None: returns file content as bytes
        #         If provided: saves to path and returns None
        #
        # The method handles:
        #   - Finding current data version if version_id not specified
        #   - Getting download URL from API  
        #   - Following presigned S3 URL
        #   - Creating parent directories if needed
        download_path = Path("downloaded_customer_data.csv")
        created_dataset.download_data(path=download_path)

        print(f"✅ Current data downloaded to: {download_path}")
        print(f"   Size: {download_path.stat().st_size} bytes")

        # Verify first few rows
        with download_path.open("r") as f:
            lines = f.readlines()
            print(f"   Preview (first 3 lines):")
            for i, line in enumerate(lines[:3]):
                print(f"     {i+1}: {line.strip()}")

        # 8. List Data Versions Operation
        print("\n8️⃣ Listing Data Versions...")

        # SDK Method: dataset.list_data_versions(page=1, page_size=10, status=None)
        #
        # This maps to: GET /dataset-data-versions?datasetIds=[{id}]&page=1&pageSize=10&...
        #
        # Parameters:
        #   page: Page number (1-based, defaults to 1)
        #   page_size: Items per page (defaults to 10)  
        #   status: Filter by status ("current", "draft", defaults to all)
        #
        # Returns: List of DatasetDataVersionModel instances directly
        versions = created_dataset.list_data_versions(
            page_size=5,
            status=None  # Show all versions
        )

        print(f"✅ Found {len(versions)} data versions:")
        for version in versions:
            status_icon = "📊" if version.status == "current" else "📝"
            row_info = f" ({version.row_count} rows)" if version.row_count else ""
            print(f"   {status_icon} Version {version.version_no}: {version.file_type.upper()}{row_info}")

        # Demonstrate downloading a specific version by ID
        if versions:
            specific_version = versions[0]  # Use the first version
            print(f"\n   📥 Demonstrating download of specific version {specific_version.version_no}...")
            
            # SDK Method: dataset.download_data(version_id="specific_id", path=None)
            # or version.download(path=None) - both work
            version_download_path = Path(f"downloaded_version_{specific_version.version_no}.csv")
            created_dataset.download_data(version_id=specific_version.dataset_data_version_id, path=version_download_path)
            print(f"   ✅ Version {specific_version.version_no} downloaded to: {version_download_path}")
            
            # Clean up this file too
            version_download_path.unlink(missing_ok=True)

        # 9. Schema Builder Operation (Advanced)
        print("\n9️⃣ Advanced Schema Builder...")

        # SDK Method: dataset.schema_builder() -> SchemaBuilder fluent API
        #
        # This provides a fluent interface for building complex schemas:
        #   builder = dataset.schema_builder()
        #   schema = (builder
        #     .add_column("name", "type", required=True, description="...")
        #     .with_parsing(delimiter=",", header_row=1)
        #     .as_current()  # or as_draft()
        #     .create())
        #
        # Methods available on SchemaBuilder:
        #   .add_column(name, type, required=False, description=None)
        #   .with_parsing(**parsing_options)  
        #   .as_current() / .as_draft()
        #   .create() -> DatasetSchemaVersionModel
        builder = created_dataset.schema_builder()
        advanced_schema = (builder
            .add_column("customer_id", "int", required=True, description="Primary key")
            .add_column("name", "string", required=True, description="Full name")  
            .add_column("email", "string", required=True, description="Contact email")
            .add_column("signup_date", "date", required=True, description="Registration date")
            .add_column("total_orders", "int", required=False, description="Order count")
            .add_column("lifetime_value", "float", required=False, description="CLV in USD")
            .add_column("is_active", "boolean", required=False, description="Active status")
            .with_parsing(delimiter=",", header_row=1, encoding="utf-8")
            .as_draft()  # Create as draft first
            .create())

        print("✅ Advanced schema created with builder!")
        print(f"   Schema ID: {advanced_schema.dataset_schema_version_id}")
        print(f"   Status: {advanced_schema.status}")
        print(f"   Columns: {len(advanced_schema.columns)}")

        # 10. Dataset Information and Rich Methods
        print("\n🔟 Dataset Information & Rich Methods...")

        # DatasetModel provides rich properties and methods without additional API calls:
        # Properties: dataset_id, name, description, record_count, processing_status, etc.
        # Rich methods: upload_data(), download_data(), create_schema(), etc.
        # Schema access: get_current_schema(), schema_builder()
        # Management: update(), delete()
        print(f"   Dataset ID: {created_dataset.dataset_id}")
        print(f"   Name: {created_dataset.name}")
        print(f"   Record Count: {created_dataset.record_count}")
        print(f"   Processing Status: {created_dataset.processing_status}")
        print(f"   Created: {created_dataset.created_at}")
        print(f"   Updated: {created_dataset.updated_at}")

        # Get current schema information
        current_schema = created_dataset.get_current_schema()
        if current_schema:
            print(f"   Current Schema: {current_schema.dataset_schema_version_id}")
            print(f"   Schema Status: {current_schema.status}")
        else:
            print("   Current Schema: None")

        # 11. Update Dataset Operation
        print("\n1️⃣1️⃣ Updating Dataset...")

        # SDK Method: dataset.update(name=None, description=None, should_process=None, **kwargs)
        #
        # This maps to: PATCH /datasets/{id}
        #
        # Parameters:
        #   name: New dataset name
        #   description: New description  
        #   should_process: Whether to trigger processing workflow
        #   **kwargs: Additional properties to update
        #
        # Returns: Updated DatasetModel instance
        created_dataset.update(
            name="Updated Customer Analytics Dataset",
            description="Enhanced customer data with advanced schema",
            should_process=True
        )

        # Important: Refetch the dataset to show the actual updated values
        print("   Refetching dataset to show updated properties...")
        created_dataset = client.datasets.retrieve(created_dataset.dataset_id)

        print("✅ Dataset updated successfully!")
        print(f"   New Name: {created_dataset.name}")
        print(f"   New Description: {created_dataset.description}")
        print(f"   Processing Status: {created_dataset.processing_status}")
        print(f"   Should Process Triggered: {created_dataset.processing_status in ['processing', 'needs-processing']}")

        print("\n🎉 Dataset operations completed successfully!")
        print("\nSummary of SDK Methods Used:")
        print("  • client.datasets.create() - Create new dataset")
        print("  • dataset.upload_data() - Upload CSV data")
        print("  • dataset.create_schema() - Create manual schema")
        print("  • dataset.create_schema_from_sample() - Auto-infer schema")
        print("  • dataset.schema_builder() - Fluent schema API")
        print("  • client.datasets.list() - List datasets with filtering")
        print("  • dataset.download_data() - Download current/specific version")
        print("  • dataset.list_data_versions() - List all data versions")
        print("  • dataset.get_current_schema() - Access current schema")
        print("  • dataset.update() - Update dataset properties")

    except APIError as e:
        print(f"❌ API Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1

    finally:
        # Clean up: Delete the created dataset
        if created_dataset:
            try:
                print("\n🗑️  Cleaning up: Deleting created dataset...")
                
                # SDK Method: dataset.delete()
                #
                # This maps to: DELETE /datasets/{id}
                # Permanently deletes the dataset and all its data versions
                # Alternative: client.datasets.delete(dataset_id)
                created_dataset.delete()
                print("✅ Dataset deleted successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete dataset: {e}")

        # Clean up local files
        try:
            csv_file.unlink(missing_ok=True)
            Path("downloaded_customer_data.csv").unlink(missing_ok=True)
            print("🧹 Cleaned up local files")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up local files: {e}")

    return 0


if __name__ == "__main__":
    exit(main())