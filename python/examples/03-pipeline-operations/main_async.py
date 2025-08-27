#!/usr/bin/env python3
"""
Async Pipeline Operations Example - Moderately AI Python SDK

This example demonstrates the complete pipeline operations workflow using the async SDK,
showing the exact method mappings from REST API endpoints to async SDK methods.

REST API vs Async SDK Method Mapping:
- REST: POST /pipelines
  SDK:  await client.pipelines.create(name="Pipeline Name")

- REST: POST /pipeline-configuration-versions
  SDK:  await pipeline.create_configuration_version(configuration={...})

- REST: POST /pipeline-executions
  SDK:  await config_version.execute(pipeline_input={...}) or await pipeline.execute({...})

- REST: GET /pipeline-executions/{id}
  SDK:  await client.pipeline_executions.retrieve(execution_id)

- REST: GET /pipelines
  SDK:  await client.pipelines.list()

- REST: DELETE /pipelines/{id}
  SDK:  await pipeline.delete() or await client.pipelines.delete(pipeline_id)

Usage:
    dotenvx run -- python main_async.py
"""

import asyncio
import json
import time

from moderatelyai_sdk import AsyncModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError


def create_sample_pipeline_config():
    """Create a sample pipeline configuration based on working echo demo."""
    pipeline_config = {
        "id": "echo_demo_async",
        "name": "Async Echo Demo",
        "description": "Simple echo pipeline that demonstrates external input injection (async version). Takes a string input from CLI and outputs it unchanged. Pipeline flow: External Input → Input Block → Output Block. Type flow: string → string",
        "version": "1.0.0",
        "blocks": {
            "user_input": {
                "id": "user_input",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "description": "User-provided text input",
                    }
                },
            },
            "echo_result": {
                "id": "echo_result",
                "type": "output",
                "config": {"name": "echoed_message"},
            },
        },
        "connections": [
            {
                "source_port": "data",
                "target_port": "data",
                "source_block_id": "user_input",
                "target_block_id": "echo_result",
            }
        ],
    }

    print(
        f"✅ Created sample pipeline configuration ({len(json.dumps(pipeline_config))} characters)"
    )
    return pipeline_config


def create_sample_input_data():
    """Create sample input data for pipeline execution."""
    sample_input = {
        "user_input": "Hello from the Moderately AI SDK async pipeline example!"
    }

    print(f"✅ Created sample input data: '{sample_input['user_input']}'")
    return sample_input


async def main():
    """Demonstrate complete async pipeline operations workflow."""
    print("🚀 Async Pipeline Operations Example - Moderately AI SDK")
    print("=" * 60)

    try:
        # Initialize the async SDK client
        # This reads MODERATELY_API_KEY and MODERATELY_TEAM_ID from environment
        print("\n1️⃣ Initializing Async SDK Client...")
        async with AsyncModeratelyAI() as client:
            print(f"✅ Async client initialized for team: {client.team_id}")

            # Create sample data for testing
            pipeline_config = create_sample_pipeline_config()
            input_data = create_sample_input_data()
            created_pipeline = None

            try:
                # 2. Create Pipeline Operation
                print("\n2️⃣ Creating Pipeline...")

                # Async SDK Method: await client.pipelines.create(name, description=None, **kwargs)
                #
                # This maps to: POST /pipelines
                # {
                #   "name": "Document Processing Pipeline",
                #   "description": "Processes documents through analysis",
                #   "teamId": "{client.team_id}"
                # }
                #
                # Parameters:
                #   name: Required pipeline name
                #   description: Optional description
                #   **kwargs: Additional pipeline properties
                #
                # Returns: PipelineAsyncModel instance with rich async methods
                timestamp = int(time.time())
                created_pipeline = await client.pipelines.create(
                    name=f"Async Document Processing Pipeline {timestamp}",
                    description="Sample document processing pipeline for async SDK demonstration",
                )

                print("✅ Pipeline created successfully!")
                print(f"   Pipeline ID: {created_pipeline.pipeline_id}")
                print(f"   Name: {created_pipeline.name}")
                print(f"   Description: {created_pipeline.description}")
                print(f"   Team ID: {created_pipeline.team_id}")
                print(f"   Created: {created_pipeline.created_at}")

                # 3. Create Configuration Version Operation
                print("\n3️⃣ Creating Configuration Version...")
                print(f"   Configuration blocks: {len(pipeline_config['blocks'])}")
                print(
                    f"   Configuration connections: {len(pipeline_config['connections'])}"
                )

                # Async SDK Method: await pipeline.create_configuration_version(configuration, **kwargs)
                #
                # This maps to: POST /pipeline-configuration-versions
                # {
                #   "pipelineId": "{pipeline_id}",
                #   "configuration": {...blocks and connections...}
                # }
                #
                # Parameters:
                #   configuration: Required pipeline configuration dict with blocks/connections
                #   **kwargs: Additional version metadata
                #
                # Returns: PipelineConfigurationVersionAsyncModel instance
                config_version = await created_pipeline.create_configuration_version(
                    configuration=pipeline_config,
                    status="draft",  # Create as draft first
                )

                print("✅ Configuration version created successfully!")
                print(f"   Version ID: {config_version.configuration_version_id}")
                print(f"   Pipeline ID: {config_version.pipeline_id}")
                print(f"   Status: {config_version.status}")
                print(f"   Version: {config_version.version}")

                # Show configuration summary
                config = config_version.configuration
                print(f"   Configuration Summary:")
                print(f"     • Blocks: {len(config.get('blocks', {}))}")
                print(f"     • Connections: {len(config.get('connections', []))}")
                print(f"     • Pipeline Name: {config.get('name', 'N/A')}")

                # 4. Validate Configuration Operation
                print("\n4️⃣ Validating Configuration...")

                # Async SDK Method: await config_version.validate()
                #
                # This maps to: POST /pipeline-configuration-versions/validate
                # { "configuration": {...} }
                #
                # Returns: Dict with validation results
                validation_result = await config_version.validate()

                print("✅ Configuration validation completed!")
                is_valid = validation_result.get("valid", False)
                print(f"   Valid: {is_valid}")

                errors = validation_result.get("errors", [])
                warnings = validation_result.get("warnings", [])

                if errors:
                    print(f"   Errors ({len(errors)}):")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"     • {error}")

                if warnings:
                    print(f"   Warnings ({len(warnings)}):")
                    for warning in warnings[:3]:  # Show first 3 warnings
                        print(f"     • {warning}")

                if not errors and not warnings:
                    print("   No errors or warnings found")

                # 5. Execute Pipeline Operation (Method 1: Using ConfigurationVersionAsyncModel)
                print(
                    "\n5️⃣ Executing Pipeline (Method 1: Async Configuration Version)..."
                )
                print(f"   Input text: {input_data['user_input']}")
                print(f"   Input summary: Echo user input text")

                # Async SDK Method: await config_version.execute(pipeline_input, pipeline_input_summary, block=False, **kwargs)
                #
                # This maps to: POST /pipeline-executions
                # {
                #   "pipelineConfigurationVersionId": "{version_id}",
                #   "pipelineInput": {...input data...},
                #   "pipelineInputSummary": "Human readable summary"
                # }
                #
                # Parameters:
                #   pipeline_input: Required input data dict
                #   pipeline_input_summary: Required human-readable summary
                #   block: If True, wait for completion (defaults to False)
                #   timeout: Maximum wait time in seconds (only with block=True)
                #   poll_interval: How often to check status (only with block=True)
                #   show_progress: Show progress updates (only with block=True)
                #   **kwargs: Additional execution properties
                #
                # Returns: PipelineExecutionAsyncModel instance
                execution = await config_version.execute(
                    pipeline_input=input_data,
                    pipeline_input_summary="Echo user input text through the async pipeline",
                    block=True,  # Wait for completion to demonstrate full workflow
                    timeout=60,  # 60 second timeout
                    show_progress=True,  # Show progress updates
                )

                print("✅ Async pipeline execution completed!")
                print(f"   Execution ID: {execution.execution_id}")
                print(
                    f"   Configuration Version ID: {execution.configuration_version_id}"
                )
                print(f"   Status: {execution.status}")
                print(f"   Created: {execution.created_at}")
                print(f"   Completed: {execution.completed_at}")
                print(f"   Is Completed: {execution.is_completed}")
                print(f"   Is Running: {execution.is_running}")

                # 6. Get Pipeline Output
                print("\n6️⃣ Getting Pipeline Output...")

                # Async SDK Method: await execution.get_output()
                #
                # This maps to: GET /pipeline-executions/{execution_id}/output
                #
                # Returns: Pipeline output data (handles both inline and S3-stored outputs with async HTTP)
                try:
                    output = await execution.get_output()
                    print(f"✅ Pipeline output retrieved!")
                    if output:
                        print(f"   Output: {output}")
                    else:
                        print("   Output: No output available")
                except Exception as e:
                    print(f"⚠️  Could not retrieve output: {e}")

                # Show final execution details
                print(f"   Final Status: {execution.status}")
                print(
                    f"   Total Runtime: {execution.created_at} → {execution.completed_at}"
                )
                if execution.progress_percentage is not None:
                    print(f"   Progress: {execution.progress_percentage:.1f}% complete")

                # 7. List Pipeline Executions Operation
                print("\n7️⃣ Listing Pipeline Executions...")

                # Async SDK Method: await client.pipeline_executions.list(**filters)
                #
                # This maps to: GET /pipeline-executions?page=1&pageSize=10&...
                #
                # Parameters:
                #   pipeline_ids: Filter by specific pipeline IDs
                #   pipeline_configuration_version_ids: Filter by config version IDs
                #   pipeline_execution_ids: Filter by specific execution IDs
                #   status: Filter by single execution status
                #   statuses: Filter by multiple execution statuses
                #   page: Page number (1-based)
                #   page_size: Items per page (defaults to 10)
                #   order_by: Sort field ("createdAt", "updatedAt", "startedAt")
                #   order_direction: "asc" or "desc"
                #
                # Returns: Dict with "items" (list of PipelineExecutionAsyncModel) and "pagination" metadata
                executions_response = await client.pipeline_executions.list(
                    pipeline_ids=[created_pipeline.pipeline_id],
                    page_size=5,
                    order_direction="desc",  # Most recent first
                )

                executions = executions_response["items"]
                pagination = executions_response.get("pagination", {})

                total_pages = pagination.get(
                    "totalPages", pagination.get("total_pages", 1)
                )
                print(
                    f"✅ Found {len(executions)} executions (page 1 of {total_pages}):"
                )
                for exec_item in executions[:3]:  # Show first 3
                    # Status icons
                    if exec_item.is_completed:
                        status_icon = "✅"
                    elif exec_item.is_running:
                        status_icon = "⏳"
                    elif exec_item.is_failed:
                        status_icon = "❌"
                    elif exec_item.is_cancelled:
                        status_icon = "⚫"
                    else:
                        status_icon = "📋"  # Pending

                    # Progress info
                    progress_info = ""
                    if exec_item.progress_percentage is not None:
                        progress_info = f" ({exec_item.progress_percentage:.1f}%)"

                    print(
                        f"   {status_icon} {exec_item.execution_id[:8]}... - {exec_item.status}{progress_info}"
                    )

                # 8. List Pipeline Configuration Versions Operation
                print("\n8️⃣ Listing Configuration Versions...")

                # Async SDK Method: await pipeline.list_configuration_versions()
                #
                # This maps to: GET /pipeline-configuration-versions?pipelineIds=[{pipeline_id}]
                #
                # Returns: List of PipelineConfigurationVersionAsyncModel instances
                config_versions = await created_pipeline.list_configuration_versions()

                print(f"✅ Found {len(config_versions)} configuration versions:")
                for version in config_versions:
                    status_icon = "📄" if version.status == "current" else "📝"
                    version_info = f" (v{version.version})" if version.version else ""
                    print(
                        f"   {status_icon} {version.configuration_version_id[:8]}... - {version.status}{version_info}"
                    )

                # 9. Clone Configuration Version Operation
                print("\n9️⃣ Cloning Configuration Version...")

                # Async SDK Method: await config_version.clone()
                #
                # This maps to: POST /pipeline-configuration-versions/{version_id}/clone
                #
                # Returns: New PipelineConfigurationVersionAsyncModel instance (cloned)
                cloned_version = await config_version.clone()

                print("✅ Configuration version cloned successfully!")
                print(
                    f"   Original Version ID: {config_version.configuration_version_id}"
                )
                print(
                    f"   Cloned Version ID: {cloned_version.configuration_version_id}"
                )
                print(f"   Cloned Status: {cloned_version.status}")
                print(f"   Cloned Version: {cloned_version.version}")

                # Modify the cloned configuration
                print("\n   📝 Modifying cloned configuration...")
                modified_config = cloned_version.configuration.copy()

                # Add metadata to show it's the async version
                modified_config["description"] = (
                    "Async version of echo pipeline with enhanced logging"
                )
                modified_config["version"] = "1.1.0"  # Increment version

                # Update the cloned version
                updated_clone = await cloned_version.update(
                    configuration=modified_config
                )
                print(f"   ✅ Cloned version updated with new parameters!")
                print(f"   Updated Version: {updated_clone.version}")

                # 10. List Pipelines Operation
                print("\n🔟 Listing Pipelines...")

                # Async SDK Method: await client.pipelines.list(**filters)
                #
                # This maps to: GET /pipelines?teamIds={team_id}&page=1&pageSize=10&...
                #
                # Parameters:
                #   pipeline_ids: Filter by specific pipeline IDs
                #   name_like: Filter by pipelines with names containing text
                #   page: Page number (1-based)
                #   page_size: Items per page (defaults to 10)
                #   order_by: Sort field ("name", "createdAt", "updatedAt")
                #   order_direction: "asc" or "desc"
                #
                # Returns: Dict with "items" (list of PipelineAsyncModel) and "pagination" metadata
                # Note: Team filtering is automatic based on client configuration
                pipelines_response = await client.pipelines.list(
                    page_size=5,
                    order_direction="desc",  # Most recent first
                    name_like="Processing",  # Filter by name containing "Processing"
                )

                pipelines = pipelines_response["items"]
                pagination = pipelines_response.get("pagination", {})

                total_pages = pagination.get(
                    "totalPages", pagination.get("total_pages", 1)
                )
                print(f"✅ Found {len(pipelines)} pipelines (page 1 of {total_pages}):")
                for pipeline in pipelines[:3]:  # Show first 3
                    print(f"   📊 {pipeline.name}")
                    print(f"      ID: {pipeline.pipeline_id}")
                    print(
                        f"      Description: {pipeline.description or 'No description'}"
                    )

                # 11. Pipeline Information & Rich Methods
                print("\n1️⃣1️⃣ Pipeline Information & Rich Async Methods...")

                # PipelineAsyncModel provides rich properties and methods without additional API calls:
                # Properties: pipeline_id, name, description, team_id, created_at, updated_at
                # Rich async methods: create_configuration_version(), list_configuration_versions(), execute()
                # Management: update(), delete()
                print(f"   Pipeline ID: {created_pipeline.pipeline_id}")
                print(f"   Name: {created_pipeline.name}")
                print(f"   Description: {created_pipeline.description}")
                print(f"   Team ID: {created_pipeline.team_id}")
                print(f"   Created: {created_pipeline.created_at}")
                print(f"   Updated: {created_pipeline.updated_at}")

                # Get the latest execution for this pipeline
                latest_executions = await created_pipeline.list_executions(page_size=1)
                if latest_executions:
                    latest = latest_executions[0]
                    print(
                        f"   Latest Execution: {latest.execution_id[:8]}... ({latest.status})"
                    )
                else:
                    print("   Latest Execution: None")

                # 12. Update Pipeline Operation
                print("\n1️⃣2️⃣ Updating Pipeline...")

                # Async SDK Method: await pipeline.update(name=None, description=None, **kwargs)
                #
                # This maps to: PATCH /pipelines/{id}
                #
                # Parameters:
                #   name: New pipeline name
                #   description: New description
                #   **kwargs: Additional properties to update
                #
                # Returns: Updated PipelineAsyncModel instance
                await created_pipeline.update(
                    name="Enhanced Async Document Processing Pipeline",
                    description="Advanced async document processing with cloned configuration support",
                )

                # Refetch to show updated values
                print("   Refetching pipeline to show updated properties...")
                created_pipeline = await client.pipelines.retrieve(
                    created_pipeline.pipeline_id
                )

                print("✅ Pipeline updated successfully!")
                print(f"   New Name: {created_pipeline.name}")
                print(f"   New Description: {created_pipeline.description}")

                # 13. Alternative Execution Methods
                print("\n1️⃣3️⃣ Alternative Async Execution Methods...")
                print("   ✅ Blocking execution (demonstrated above)")
                print("   Alternative: Non-blocking execution would use:")
                print(
                    "   execution = await config_version.execute(input_data, summary, block=False)"
                )
                print(
                    "   then use await execution.refresh() to monitor progress manually"
                )

                print("\n🎉 Async pipeline operations completed successfully!")
                print("\nSummary of Async SDK Methods Used:")
                print("  • await client.pipelines.create() - Create new pipeline")
                print(
                    "  • await pipeline.create_configuration_version() - Create configuration"
                )
                print("  • await config_version.validate() - Validate configuration")
                print(
                    "  • await config_version.execute(block=True) - Execute pipeline and wait for completion"
                )
                print(
                    "  • await execution.get_output() - Retrieve pipeline execution results"
                )
                print("  • await config_version.clone() - Clone configuration")
                print("  • await client.pipeline_executions.list() - List executions")
                print(
                    "  • await pipeline.list_configuration_versions() - List versions"
                )
                print(
                    "  • await client.pipelines.list() - List pipelines with filtering"
                )
                print("  • await pipeline.update() - Update pipeline properties")

            except APIError as e:
                print(f"❌ API Error: {e}")
                return 1
            except Exception as e:
                print(f"❌ Unexpected Error: {e}")
                return 1

            finally:
                # Clean up: Delete the created pipeline
                if created_pipeline:
                    try:
                        print("\n🗑️  Cleaning up: Deleting created pipeline...")

                        # Async SDK Method: await pipeline.delete()
                        #
                        # This maps to: DELETE /pipelines/{id}
                        # Permanently deletes the pipeline and all its configuration versions
                        # Alternative: await client.pipelines.delete(pipeline_id)
                        await created_pipeline.delete()
                        print("✅ Pipeline deleted successfully")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete pipeline: {e}")

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
