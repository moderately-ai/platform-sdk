#!/usr/bin/env python3
"""
Variance Analysis Example - Moderately AI Python SDK

This example demonstrates how to analyze employment contract clauses for variances
from standard/benchmark terms using the legal_variance_determination pipeline block.

Workflow:
1. Create datasets for clause definitions, benchmarks, variance guidance, and research materials
2. Load extracted clause data from JSON file
3. Create and execute variance analysis pipeline
4. Generate variance analysis report with findings and recommendations

Usage:
    dotenvx run -- python main.py
"""

import csv
import json
import time
from pathlib import Path

from moderatelyai_sdk import ModeratelyAI
from moderatelyai_sdk.exceptions import APIError, AuthenticationError
from moderatelyai_sdk.models.dataset import DatasetModel
from moderatelyai_sdk.models.pipeline import PipelineModel
from moderatelyai_sdk.models.pipeline_configuration_version import (
    PipelineConfigurationVersionModel,
)


def create_dataset_from_csv(
    client: ModeratelyAI, csv_path: Path, name: str, description: str
) -> DatasetModel:
    """Create a dataset from a CSV file with schema and processing."""
    print(f"\n📋 Creating {name}...")

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    timestamp = int(time.time())
    dataset = client.datasets.create(
        name=f"{name} {timestamp}",
        description=description,
    )

    # Upload data and create schema
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
        refreshed_dataset = client.datasets.retrieve(dataset.dataset_id)

        if (
            hasattr(refreshed_dataset, "processing_status")
            and refreshed_dataset.processing_status == "completed"
        ):
            print("   ✅ Dataset processing complete")
            break
        elif wait_time > 0:
            print(f"   ⏳ Still processing... ({wait_time}s)")

        time.sleep(5)
        wait_time += 5

    if wait_time >= max_wait:
        print("   ⚠️  Dataset processing timeout - continuing anyway")

    return dataset


def create_variance_analysis_pipeline(
    client: ModeratelyAI,
) -> tuple[PipelineModel, PipelineConfigurationVersionModel]:
    """Create variance analysis pipeline configuration."""
    print("\n🔧 Creating variance analysis pipeline...")

    pipeline_config = {
        "id": "variance_analysis",
        "name": "Variance Analysis",
        "description": "Pipeline for analyzing variances in employment contract clauses",
        "version": "1.0.0",
        "blocks": {
            "input_extracted_clauses": {
                "id": "input_extracted_clauses",
                "name": "Extracted Clause Data",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["clause_number", "excerpts"],
                            "properties": {
                                "excerpts": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["text", "section"],
                                        "properties": {
                                            "text": {"type": "string"},
                                            "section": {"type": "string"},
                                        },
                                    },
                                },
                                "clause_number": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "input_clause_definitions": {
                "id": "input_clause_definitions",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "format": "dataset",
                        "description": "Clause definitions dataset ID",
                    },
                },
            },
            "input_benchmark_clauses": {
                "id": "input_benchmark_clauses",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "array",
                        "items": {"type": "string", "format": "dataset"},
                        "description": "Benchmark clause datasets",
                    },
                },
            },
            "input_research_materials": {
                "id": "input_research_materials",
                "name": "Research Datasets",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "array",
                        "items": {"type": "string", "format": "dataset"},
                        "description": "Generic research datasets for semantic search (regulations, statutes, case law)",
                    },
                },
            },
            "input_clause_variance_guidance": {
                "id": "input_clause_variance_guidance",
                "name": "Clause Variance Guidance",
                "type": "input",
                "config": {
                    "json_schema": {
                        "type": "string",
                        "format": "dataset",
                        "description": "Clause-specific variance guidance dataset (requires clause_number field)",
                    },
                },
            },
            "variance_determination": {
                "id": "variance_determination",
                "type": "legal_variance_determination",
                "config": {
                    "general_instructions": """You are analyzing employment contracts in Ontario, Canada under the Employment Standards Act, 2000 (ESA) and common law principles.

LEGAL FRAMEWORK:
- ESA 2000 sets statutory minimums that CANNOT be contracted below
- Common law reasonable notice standards apply (Bardal factors)
- Small employer context (< 5 employees) allows some practical flexibility
- Personal care services governed by PHIPA privacy requirements

RISK EVALUATION PRIORITIES:
1. ESA Compliance (FUNDAMENTAL):
   - Minimum wage compliance ($17.20/hour Ontario 2024)
   - Overtime and hours of work (ESA Part VIII)
   - Vacation entitlements (ESA Part XI)
   - Termination notice/pay (ESA Part XV)
   - Any provision below ESA minimums → MODIFY (fundamental)

2. Common Law Standards (MATERIAL):
   - Reasonable notice provisions (Bardal: character, length of service, age, availability)
   - Termination clauses must not contract below common law
   - Constructive dismissal risks (significant changes to role, location, compensation)
   - Missing or unclear termination provisions → MODIFY (material)

3. Occupational Health & Safety (MATERIAL):
   - OHSA worker safety obligations must be explicit
   - Duty of care for vulnerable clients
   - Missing OHSA references → MODIFY (material)

4. Industry Standards - Personal Care (NOTABLE):
   - Privacy/confidentiality per PHIPA required
   - Duty descriptions appropriate for role level
   - Administrative clarity issues → NOTABLE (flag but may accept)

MATERIALITY THRESHOLDS:
- Compensation below ESA minimums → FUNDAMENTAL
- Missing exempt/non-exempt status → FUNDAMENTAL
- Termination provisions below statutory minimums → FUNDAMENTAL
- Missing OHSA safety obligations → MATERIAL
- Unclear privacy/confidentiality obligations → MATERIAL
- Vague duty descriptions → NOTABLE
- Stylistic variations from benchmarks → DE_MINIMIS

SPECIAL CONSIDERATIONS:
- Small employer: Practical flexibility in administrative procedures acceptable
- Vulnerable client population: Privacy and safety protections essential
- Personal care context: Explicit duty of care obligations required
- Employment relationship: Balance statutory protections with operational needs

DECISION GUIDANCE:
- ACCEPT: All ESA minimums met, reasonable notice protected, core obligations clear
- MODIFY: ESA violations, common law gaps, missing statutory references, fundamental ambiguities
- When in doubt about compliance, err on side of MODIFY to protect employee rights
""",
                    "clause_definition": "",
                    "transaction_context": "Employment agreement for attendant care worker in Ontario, Canada. Personal care services for individual with physical disability. Small employer (under 5 employees). 2025 agreement subject to Ontario Employment Standards Act and common law principles.",
                },
            },
            "output_variance_results": {
                "id": "output_variance_results",
                "type": "output",
                "config": {"name": "variance_results"},
            },
        },
        "connections": [
            {
                "source_block_id": "input_extracted_clauses",
                "source_port": "data",
                "target_block_id": "variance_determination",
                "target_port": "extracted_clauses",
            },
            {
                "source_block_id": "input_clause_definitions",
                "source_port": "data",
                "target_block_id": "variance_determination",
                "target_port": "clause_definition_dataset_id",
            },
            {
                "source_block_id": "input_benchmark_clauses",
                "source_port": "data",
                "target_block_id": "variance_determination",
                "target_port": "benchmark_dataset_ids",
            },
            {
                "source_block_id": "input_research_materials",
                "source_port": "data",
                "target_block_id": "variance_determination",
                "target_port": "research_dataset_ids",
            },
            {
                "source_block_id": "input_clause_variance_guidance",
                "source_port": "data",
                "target_block_id": "variance_determination",
                "target_port": "clause_variance_guidance_dataset_id",
            },
            {
                "source_block_id": "variance_determination",
                "source_port": "results",
                "target_block_id": "output_variance_results",
                "target_port": "data",
            },
        ],
    }

    timestamp = int(time.time())
    pipeline = client.pipelines.create(
        name=f"Variance Analysis Pipeline {timestamp}",
        description="Legal variance determination for employment contracts",
    )

    config_version = pipeline.create_configuration_version(
        configuration=pipeline_config, status="current"
    )

    print(f"   ✅ Created: {pipeline.pipeline_id}")
    return pipeline, config_version


def execute_pipeline(
    config_version: PipelineConfigurationVersionModel,
    extracted_clauses: list,
    clause_definitions_dataset: DatasetModel,
    benchmark_dataset: DatasetModel,
    variance_guidance_dataset: DatasetModel,
    research_dataset: DatasetModel,
):
    """Execute the variance analysis pipeline."""
    print("\n🚀 Executing variance analysis pipeline...")

    pipeline_input = {
        "input_extracted_clauses": extracted_clauses,
        "input_clause_definitions": clause_definitions_dataset.dataset_id,
        "input_benchmark_clauses": [benchmark_dataset.dataset_id],
        "input_research_materials": [research_dataset.dataset_id],
        "input_clause_variance_guidance": variance_guidance_dataset.dataset_id,
    }

    print(f"   📋 Analyzing {len(extracted_clauses)} extracted clauses")
    print(f"   📊 Using clause definitions: {clause_definitions_dataset.dataset_id}")
    print(f"   📈 Using benchmarks: {benchmark_dataset.dataset_id}")
    print(f"   📝 Using clause variance guidance: {variance_guidance_dataset.dataset_id}")
    print(f"   📚 Using research materials: {research_dataset.dataset_id}")

    execution = config_version.execute(
        pipeline_input=pipeline_input,
        pipeline_input_summary="Variance analysis on employment agreement clauses",
        block=True,
        timeout=300,
        show_progress=True,
    )

    print(f"   ✅ Completed: {execution.status}")

    if execution.status == "failed":
        print(f"   📋 Execution ID: {execution.execution_id}")
        if hasattr(execution, "_data"):
            error_data = execution._data
            print(f"   ❌ Error details: {error_data}")

    try:
        output = execution.get_output()
        print(f"   📊 Output received")

        # Save output to JSON file
        output_file = Path(__file__).parent / "output" / "variance_results.json"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"   💾 JSON results saved to: {output_file}")

        # Generate CSV report
        if "variance_results" in output:
            generate_variance_report(output["variance_results"])

    except Exception as e:
        print(f"   ⚠️  Could not get output: {e}")

    return execution


def generate_variance_report(variance_results: list):
    """Generate a CSV report from variance analysis results."""
    print("\n📊 Generating variance report...")

    csv_file = Path(__file__).parent / "output" / "variance_report.csv"

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "clause_number",
                "decision",
                "confidence",
                "reasoning",
                "drafting_instructions",
                "research_question_count",
            ]
        )

        # Process variance results - now a list of ClauseVarianceDetermination objects
        for result in variance_results:
            clause_num = result.get("clause_number", "")
            decision = result.get("decision", "")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "")

            # Join drafting instructions into a single string
            drafting_instructions = result.get("drafting_instructions", [])
            if isinstance(drafting_instructions, list):
                drafting_instructions_str = " | ".join(drafting_instructions)
            else:
                drafting_instructions_str = str(drafting_instructions)

            # Count research insights
            research_insights = result.get("research_insights", [])
            research_count = len(research_insights) if isinstance(research_insights, list) else 0

            writer.writerow(
                [
                    clause_num,
                    decision,
                    f"{confidence:.2f}",
                    reasoning,
                    drafting_instructions_str,
                    research_count,
                ]
            )

    print(f"   💾 CSV report saved to: {csv_file}")


def main():
    """Run the variance analysis example."""
    print("🚀 Variance Analysis Example")
    print("=" * 50)

    try:
        # Initialize client
        print("\n1️⃣ Initializing SDK Client...")
        client = ModeratelyAI()
        print(f"✅ Client ready for team: {client.team_id}")

        # Setup datasets
        data_dir = Path(__file__).parent / "data"

        clause_definitions_dataset = create_dataset_from_csv(
            client,
            data_dir / "clause_definitions.csv",
            "Clause Definitions",
            "Legal clause definitions for variance analysis",
        )

        benchmark_dataset = create_dataset_from_csv(
            client,
            data_dir / "benchmark_clauses.csv",
            "Benchmark Clauses",
            "Standard benchmark terms for employment contract clauses",
        )

        variance_guidance_dataset = create_dataset_from_csv(
            client,
            data_dir / "variance_guidance.csv",
            "Variance Guidance",
            "Guidance for evaluating clause variances and materiality",
        )

        research_dataset = create_dataset_from_csv(
            client,
            data_dir / "research_materials.csv",
            "Legal Research Materials",
            "Case law, statutes, and legal research for variance analysis",
        )

        # Load extracted clauses
        print("\n📄 Loading extracted clause data...")
        with open(data_dir / "extracted_clauses.json", "r", encoding="utf-8") as f:
            extracted_clauses = json.load(f)
        print(f"   ✅ Loaded {len(extracted_clauses)} clauses")

        # Create pipeline
        pipeline, config_version = create_variance_analysis_pipeline(client)

        # Execute pipeline
        try:
            execution = execute_pipeline(
                config_version,
                extracted_clauses,
                clause_definitions_dataset,
                benchmark_dataset,
                variance_guidance_dataset,
                research_dataset,
            )
        except Exception as pipeline_error:
            print(f"   ❌ Pipeline execution error: {pipeline_error}")
            print(f"   📋 Error type: {type(pipeline_error).__name__}")
            if hasattr(pipeline_error, "__dict__"):
                print(f"   📋 Error details: {pipeline_error.__dict__}")
            raise

        print("\n🎉 Variance analysis completed!")
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
        if hasattr(e, 'response_data') and e.response_data:
            print(f"   📋 Response data: {json.dumps(e.response_data, indent=2)}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            if "clause_definitions_dataset" in locals():
                clause_definitions_dataset.delete()
                print("   ✅ Deleted clause definitions dataset")
        except:
            pass

        try:
            if "benchmark_dataset" in locals():
                benchmark_dataset.delete()
                print("   ✅ Deleted benchmark dataset")
        except:
            pass

        try:
            if "variance_guidance_dataset" in locals():
                variance_guidance_dataset.delete()
                print("   ✅ Deleted variance guidance dataset")
        except:
            pass

        try:
            if "research_dataset" in locals():
                research_dataset.delete()
                print("   ✅ Deleted research dataset")
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
