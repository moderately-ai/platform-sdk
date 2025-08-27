#!/usr/bin/env python3
"""
Dataset Chat Example - Moderately AI Python SDK

Simple workflow:
1. Create context dataset
2. Create and execute chat pipeline

Usage:
    dotenvx run -- python main.py
"""

import time
from pathlib import Path

from moderatelyai_sdk import ModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError
from moderatelyai_sdk.models.dataset import DatasetModel
from moderatelyai_sdk.models.pipeline import PipelineModel
from moderatelyai_sdk.models.pipeline_configuration_version import (
    PipelineConfigurationVersionModel,
)


def create_context_dataset(client: ModeratelyAI) -> DatasetModel:
    """Create context dataset."""
    print("\n📄 Creating context dataset...")

    csv_path = Path(__file__).parent / "data" / "context.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    timestamp = int(time.time())
    dataset = client.datasets.create(
        name=f"Dataset Chat {timestamp}",
        description="Dataset chat",
    )

    data_version = dataset.upload_data(file=csv_path, file_type="csv", status="current")
    schema = dataset.create_schema_from_sample(
        sample_file=csv_path, status="current", header_row=1
    )

    print(f"   ✅ Created: {dataset.dataset_id}")
    print(f"   📊 Data version: {data_version.dataset_data_version_id}")
    print(f"   📋 Schema: {schema.dataset_schema_version_id}")

    # Trigger dataset processing
    print("   🔄 Triggering dataset processing...")
    dataset.update(should_process=True)

    # Wait for dataset processing to complete
    print("   ⏳ Waiting for dataset processing...")
    max_wait = 60  # 60 seconds timeout
    wait_time = 0

    while wait_time < max_wait:
        # Refresh dataset to get latest status
        refreshed_dataset = client.datasets.retrieve(dataset.dataset_id)

        # Check if processing is complete
        if (
            hasattr(refreshed_dataset, "processing_status")
            and refreshed_dataset.processing_status == "completed"
        ):
            print("   ✅ Dataset processing complete")
            break
        elif wait_time > 0:  # Don't print on first check
            print(f"   ⏳ Still processing... ({wait_time}s)")

        time.sleep(5)
        wait_time += 5

    if wait_time >= max_wait:
        print("   ⚠️  Dataset processing timeout - continuing anyway")

    return dataset


def create_clause_extraction_pipeline(
    client: ModeratelyAI,
) -> tuple[PipelineModel, PipelineConfigurationVersionModel]:
    """Create clause extraction pipeline."""
    print("\n🔧 Creating clause extraction pipeline...")

    pipeline_config = {
        "id": "clause_extraction",
        "name": "Clause Extraction",
        "description": "Pipeline for extracting clauses from PDF documents using the clause_extraction molecule block.",
        "version": "0.1.0",
        "blocks": {
            "context_datasets": {
                "id": "context_datasets",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "dataset",
                            "description": "Context dataset ID for legal domain context",
                        },
                    },
                },
            },
            "user_input": {
                "id": "user_input",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "Message to send to the dataset",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "description": "Role of the message",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Content of the message",
                                },
                            },
                        },
                    },
                },
            },
            "llm": {
                "id": "llm",
                "type": "llm",
                "config": {
                    "provider": "anthropic",
                    "model": "medium",
                },
            },
            "output": {
                "id": "output",
                "type": "output",
                "config": {"name": "output"},
            },
        },
        "connections": [
            # Connect datasets to the LLM block
            {
                "source_block_id": "context_datasets",
                "source_port": "data",
                "target_block_id": "llm",
                "target_port": "datasets",
            },
            # Connect user input to the LLM block
            {
                "source_block_id": "user_input",
                "source_port": "data",
                "target_block_id": "llm",
                "target_port": "messages",
            },
            # Connect LLM answer to the output block
            {
                "source_block_id": "llm",
                "source_port": "response",
                "target_block_id": "output",
                "target_port": "data",
            },
        ],
    }

    timestamp = int(time.time())
    pipeline = client.pipelines.create(
        name=f"Chat w/ Dataset Pipeline {timestamp}",
        description="Chat with a dataset",
    )

    config_version = pipeline.create_configuration_version(
        configuration=pipeline_config, status="current"
    )

    print(f"   ✅ Created: {pipeline.pipeline_id}")
    return pipeline, config_version


def execute_pipeline(
    config_version: PipelineConfigurationVersionModel,
    context_dataset: DatasetModel,
    message_history: list[dict],
):
    """Execute the clause extraction pipeline."""
    print(f"\n🚀 Executing pipeline on: {context_dataset.name}")

    pipeline_input = {
        "context_datasets": [context_dataset.dataset_id],
        "user_input": message_history,
    }

    print(f"   📄 Context: {context_dataset.dataset_id}")

    execution = config_version.execute(
        pipeline_input=pipeline_input,
        pipeline_input_summary=f"Chat with {context_dataset.name}",
        block=True,
        timeout=300,
        show_progress=True,
    )

    print(f"   ✅ Completed: {execution.status}")

    # Debug execution details
    if execution.status == "failed":
        print(f"   📋 Execution ID: {execution.execution_id}")
        if hasattr(execution, "_data"):
            error_data = execution._data
            print(f"   ❌ Error details: {error_data}")

    try:
        output = execution.get_output()
        print(f"   📊 Output: {str(output)[:100]}...")
        answer = output["output"]
        print(f"   💬 Answer: {answer}")

    except Exception as e:
        print(f"   ⚠️  Could not get output: {e}")

    return execution


def main():
    """Run the legal document extraction example."""
    print("🚀 Legal Document Extraction Example")
    print("=" * 50)

    try:
        # Initialize client
        print("\n1️⃣ Initializing SDK Client...")
        client = ModeratelyAI()
        print(f"✅ Client ready for team: {client.team_id}")

        # Setup components
        context_dataset = create_context_dataset(client)
        pipeline, config_version = create_clause_extraction_pipeline(client)

        # Enter chat loop
        print("💬 Chat with dataset, type 'exit' to quit")
        message_history = []
        while True:
            # Get user input
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break

            message_history.append({"role": "user", "content": user_input})

            # Execute pipeline
            execution = execute_pipeline(
                config_version, context_dataset, message_history
            )

            # Get answer
            answer = execution.get_output()["output"]
            print(f"Assistant:\n{answer}")

            # Add answer to message history
        print("\n🎉 Chat with dataset completed!")
        print(f"   • Pipeline: {pipeline.pipeline_id}")
        print(f"   • Execution: {execution.execution_id}")

    except (ValueError, AuthenticationError) as e:
        print(f"❌ Setup Error: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        return 1
    except APIError as e:
        print(f"❌ API Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            if "context_dataset" in locals():
                context_dataset.delete()
                print("   ✅ Deleted context dataset")
        except:
            pass

        try:
            if "pipeline" in locals():
                pipeline.delete()
                print("   ✅ Deleted pipeline")
        except:
            pass

    return 0


if __name__ == "__main__":
    exit(main())
