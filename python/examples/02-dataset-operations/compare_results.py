#!/usr/bin/env python3
"""Compare sync vs async results directly."""

import asyncio
import csv
from pathlib import Path

from moderatelyai_sdk import ModeratelyAI, AsyncModeratelyAI


def create_test_csv() -> Path:
    """Create identical test CSV for both versions."""
    sample_data = [
        ["customer_id", "name", "email", "total_orders"],
        ["1001", "Alice", "alice@example.com", "12"],
        ["1002", "Bob", "bob@example.com", "8"],  
    ]
    temp_file = Path("compare_test.csv")
    with temp_file.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sample_data)
    return temp_file


def test_sync():
    """Test sync version and return results."""
    print("🔄 Testing Sync Schema Creation")
    
    client = ModeratelyAI()
    csv_file = create_test_csv()
    
    try:
        # Create dataset and upload data
        dataset = client.datasets.create(name=f"Sync Test {int(__import__('time').time())}")
        data_version = dataset.upload_data(csv_file)
        
        # Test schema from sample
        schema = dataset.create_schema_from_sample(
            sample_file=csv_file,
            status="draft",
            header_row=1,
            sample_size=50
        )
        
        print(f"✅ Sync Results:")
        print(f"   Schema ID: {schema.dataset_schema_version_id}")
        print(f"   Columns: {len(schema.columns)}")
        print(f"   Status: {schema.status}")
        print(f"   Column data: {schema.columns}")
        
        # Cleanup
        dataset.delete()
        return len(schema.columns)
        
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return -1
    finally:
        csv_file.unlink(missing_ok=True)


async def test_async():
    """Test async version and return results."""
    print("\n🔄 Testing Async Schema Creation")
    
    async with AsyncModeratelyAI() as client:
        csv_file = create_test_csv()
        
        try:
            # Create dataset and upload data
            dataset = await client.datasets.create(name=f"Async Test {int(__import__('time').time())}")
            data_version = await dataset.upload_data(csv_file)
            
            # Test schema from sample
            schema = await dataset.create_schema_from_sample(
                sample_file=csv_file,
                status="draft", 
                header_row=1,
                sample_size=50
            )
            
            print(f"✅ Async Results:")
            print(f"   Schema ID: {schema.dataset_schema_version_id}")
            print(f"   Columns: {len(schema.columns)}")
            print(f"   Status: {schema.status}")
            print(f"   Column data: {schema.columns}")
            
            # Cleanup
            await dataset.delete()
            return len(schema.columns)
            
        except Exception as e:
            print(f"❌ Async error: {e}")
            import traceback
            traceback.print_exc()
            return -1
        finally:
            csv_file.unlink(missing_ok=True)


async def main():
    print("🔍 Comparing Sync vs Async Results\n")
    
    # Test both versions
    sync_columns = test_sync()
    async_columns = await test_async()
    
    print(f"\n📊 Summary:")
    print(f"   Sync columns: {sync_columns}")
    print(f"   Async columns: {async_columns}")
    
    if sync_columns == async_columns and sync_columns > 0:
        print("   ✅ Results match perfectly!")
    elif sync_columns == async_columns:
        print("   ⚠️  Both failed")
    else:
        print("   ❌ Results differ - need investigation")


if __name__ == "__main__":
    asyncio.run(main())