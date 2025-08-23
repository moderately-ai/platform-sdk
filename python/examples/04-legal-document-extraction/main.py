#!/usr/bin/env python3
"""
Legal Document Extraction Example - Moderately AI Python SDK

Simple workflow:
1. Upload employment agreement PDF
2. Create clause definitions dataset
3. Create context dataset
4. Create and execute clause extraction pipeline

Usage:
    dotenvx run -- python main.py
"""

import hashlib
import json
import time
from pathlib import Path

from moderatelyai_sdk import ModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError
from moderatelyai_sdk.models.dataset import DatasetModel
from moderatelyai_sdk.models.file import FileModel
from moderatelyai_sdk.models.pipeline import PipelineModel
from moderatelyai_sdk.models.pipeline_configuration_version import (
    PipelineConfigurationVersionModel,
)


def upload_employment_agreement(client: ModeratelyAI) -> FileModel:
    """Upload the employment agreement PDF."""
    print("\n📤 Uploading employment agreement PDF...")

    pdf_path = Path(__file__).parent / "data" / "employment_agreement.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"   Processing: {pdf_path.name}")

    # Check for existing file by hash
    with open(pdf_path, "rb") as f:
        file_data = f.read()
        file_hash = hashlib.sha256(file_data).hexdigest()

    print(f"   📝 File hash: {file_hash[:16]}...")

    try:
        existing_files = client.files.list(file_hashes=file_hash)["items"]
        if existing_files:
            existing_file = existing_files[0]
            print(f"   ✅ Found existing file: {existing_file.file_id}")
            return existing_file
    except Exception as e:
        print(f"   ⚠️  Could not check for duplicates: {e}")

    # Upload new file
    print(f"   📤 Uploading...")
    file_model = client.files.upload(file=pdf_path, name=pdf_path.name)
    print(f"   ✅ Uploaded: {file_model.file_id}")

    return file_model


def create_clause_definitions_dataset(client: ModeratelyAI) -> DatasetModel:
    """Create clause definitions dataset."""
    print("\n📋 Creating clause definitions dataset...")

    csv_path = Path(__file__).parent / "data" / "clause_definitions.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    timestamp = int(time.time())
    dataset = client.datasets.create(
        name=f"Clause Definitions {timestamp}",
        description="Legal clause definitions for extraction",
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
        if hasattr(refreshed_dataset, 'processing_status') and refreshed_dataset.processing_status == 'completed':
            print("   ✅ Dataset processing complete")
            break
        elif wait_time > 0:  # Don't print on first check
            print(f"   ⏳ Still processing... ({wait_time}s)")
            
        time.sleep(5)
        wait_time += 5
    
    if wait_time >= max_wait:
        print("   ⚠️  Dataset processing timeout - continuing anyway")

    return dataset


def create_context_dataset(client: ModeratelyAI) -> DatasetModel:
    """Create context dataset."""
    print("\n📄 Creating context dataset...")

    csv_path = Path(__file__).parent / "data" / "context.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    timestamp = int(time.time())
    dataset = client.datasets.create(
        name=f"Legal Context {timestamp}",
        description="Context information for legal processing",
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
        if hasattr(refreshed_dataset, 'processing_status') and refreshed_dataset.processing_status == 'completed':
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
            "pdf_file_id": {
                "id": "pdf_file_id",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "format": "file",
                        "description": "PDF File ID to analyze for clauses",
                    },
                },
            },
            "clause_definitions_dataset_id": {
                "id": "clause_definitions_dataset_id",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "format": "dataset",
                        "description": "Clause definitions dataset ID",
                    },
                },
            },
            "context_dataset_id": {
                "id": "context_dataset_id",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "description": "Context dataset ID for legal domain context",
                    },
                },
            },
            "clause_extraction_agent": {
                "id": "clause_extraction_agent",
                "type": "clause_extraction_agent",
                "config": {
                    "instructions": "Extract all clauses from the input document, focus on extracting per the clause definitions dataset.",
                },
            },
            "clause_analysis_results": {
                "id": "clause_analysis_results",
                "type": "output",
                "config": {"name": "clause_analysis_results"},
            },
        },
        "connections": [
            {
                "source_block_id": "pdf_file_id",
                "source_port": "data",
                "target_block_id": "clause_extraction_agent",
                "target_port": "file_id",
            },
            {
                "source_block_id": "clause_definitions_dataset_id",
                "source_port": "data",
                "target_block_id": "clause_extraction_agent",
                "target_port": "dataset_id",
            },
            {
                "source_block_id": "context_dataset_id",
                "source_port": "data",
                "target_block_id": "clause_extraction_agent",
                "target_port": "context_dataset_id",
            },
            {
                "source_block_id": "clause_extraction_agent",
                "source_port": "results",
                "target_block_id": "clause_analysis_results",
                "target_port": "data",
            },
        ],
    }

    timestamp = int(time.time())
    pipeline = client.pipelines.create(
        name=f"Clause Extraction Pipeline {timestamp}",
        description="Legal document analysis pipeline",
    )

    config_version = pipeline.create_configuration_version(
        configuration=pipeline_config, status="current"
    )

    print(f"   ✅ Created: {pipeline.pipeline_id}")
    return pipeline, config_version


def execute_pipeline(
    config_version: PipelineConfigurationVersionModel,
    file_model: FileModel,
    clause_definitions_dataset: DatasetModel,
    context_dataset: DatasetModel,
):
    """Execute the clause extraction pipeline."""
    print(f"\n🚀 Executing pipeline on: {file_model.name}")

    pipeline_input = {
        "pdf_file_id": file_model.file_id,
        "clause_definitions_dataset_id": clause_definitions_dataset.dataset_id,
        "context_dataset_id": context_dataset.dataset_id,
    }

    print(f"   📄 File ID: {file_model.file_id}")
    print(f"   📋 Clause definitions: {clause_definitions_dataset.dataset_id}")
    print(f"   📄 Context: {context_dataset.dataset_id}")

    execution = config_version.execute(
        pipeline_input=pipeline_input,
        pipeline_input_summary=f"Extract clauses from {file_model.name}",
        block=True,
        timeout=300,
        show_progress=True,
    )

    print(f"   ✅ Completed: {execution.status}")
    
    # Debug execution details
    if execution.status == "failed":
        print(f"   📋 Execution ID: {execution.execution_id}")
        if hasattr(execution, '_data'):
            error_data = execution._data
            print(f"   ❌ Error details: {error_data}")

    try:
        output = execution.get_output()
        print(f"   📊 Output: {str(output)[:100]}...")
        
        # Save output to JSON file
        output_file = Path(__file__).parent / "output" / "extraction_results.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Results saved to: {output_file}")
        
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
        file_model = upload_employment_agreement(client)
        clause_definitions_dataset = create_clause_definitions_dataset(client)
        context_dataset = create_context_dataset(client)
        pipeline, config_version = create_clause_extraction_pipeline(client)

        # Execute pipeline
        try:
            execution = execute_pipeline(
                config_version, file_model, clause_definitions_dataset, context_dataset
            )
        except Exception as pipeline_error:
            print(f"   ❌ Pipeline execution error: {pipeline_error}")
            print(f"   📋 Error type: {type(pipeline_error).__name__}")
            if hasattr(pipeline_error, '__dict__'):
                print(f"   📋 Error details: {pipeline_error.__dict__}")
            raise

        print("\n🎉 Legal document extraction completed!")
        print(f"   • File: {file_model.name}")
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
            if "file_model" in locals():
                file_model.delete()
                print("   ✅ Deleted file")
        except:
            pass

        try:
            if "clause_definitions_dataset" in locals():
                clause_definitions_dataset.delete()
                print("   ✅ Deleted clause definitions dataset")
        except:
            pass

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
