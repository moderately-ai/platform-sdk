#!/usr/bin/env python3
"""Test script to verify fat models work against the live API."""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import from the development version
sys.path.insert(0, str(Path(__file__).parent / "src"))

from moderatelyai_sdk import ModeratelyAI, AsyncModeratelyAI


def test_sync_fat_models():
    """Test sync fat models against live API."""
    print("🔄 Testing Sync Fat Models...")
    
    try:
        # Initialize sync client (should read from environment)
        client = ModeratelyAI()
        print(f"✅ Sync client initialized for team: {client.team_id}")
        
        # Test 1: List datasets (should return raw data)
        print("\n📊 Testing Datasets...")
        datasets_response = client.datasets.list(page_size=1)
        print(f"✅ Listed datasets: {len(datasets_response.get('items', []))} items")
        
        # Test 2: If we have datasets, get one with rich functionality
        if datasets_response.get('items'):
            dataset_id = datasets_response['items'][0]['datasetId']
            dataset = client.datasets.retrieve(dataset_id)
            print(f"✅ Retrieved dataset: {dataset.name} (ID: {dataset.dataset_id})")
            print(f"   - Record count: {dataset.record_count}")
            print(f"   - Processing status: {dataset.processing_status}")
            print(f"   - Created: {dataset.created_at}")
            
            # Test dataset methods exist
            assert hasattr(dataset, 'upload_data'), "Missing upload_data method"
            assert hasattr(dataset, 'download_data'), "Missing download_data method"
            assert hasattr(dataset, 'create_schema'), "Missing create_schema method"
            assert hasattr(dataset, 'schema_builder'), "Missing schema_builder method"
            print("✅ Dataset fat model has all expected methods")
        else:
            print("ℹ️  No datasets found to test")
        
        # Test 3: List files (should return raw data)
        print("\n📁 Testing Files...")
        files_response = client.files.list(page_size=1)
        print(f"✅ Listed files: {len(files_response.get('items', []))} items")
        
        # Test 4: If we have files, get one with rich functionality
        if files_response.get('items'):
            file_id = files_response['items'][0].get('fileId') or files_response['items'][0].get('id')
            file = client.files.retrieve(file_id)
            print(f"✅ Retrieved file: {file.name} (ID: {file.file_id})")
            print(f"   - Size: {file.file_size} bytes")
            print(f"   - MIME type: {file.mime_type}")
            print(f"   - Status: {file.status}")
            print(f"   - Is ready: {file.is_ready()}")
            print(f"   - Is document: {file.is_document()}")
            print(f"   - Extension: {file.get_extension()}")
            
            # Test file methods exist
            assert hasattr(file, 'download'), "Missing download method"
            assert hasattr(file, 'delete'), "Missing delete method"
            print("✅ File fat model has all expected methods")
        else:
            print("ℹ️  No files found to test")
        
        # Test 5: List users (should return raw data)
        print("\n👥 Testing Users...")
        users_response = client.users.list(page_size=1)
        print(f"✅ Listed users: {len(users_response.get('items', []))} items")
        
        # Test 6: If we have users, get one with rich functionality
        if users_response.get('items'):
            user_id = users_response['items'][0]['id']
            user = client.users.retrieve(user_id)
            print(f"✅ Retrieved user: {user.display_name()} (ID: {user.user_id})")
            print(f"   - Email: {user.email}")
            print(f"   - Has name: {user.has_name()}")
            print(f"   - Created: {user.formatted_created_at()}")
            print(f"   - Is recent: {user.is_recent()}")
            
            # Test user methods exist
            assert hasattr(user, 'update_profile'), "Missing update_profile method"
            assert hasattr(user, 'get_teams'), "Missing get_teams method"
            print("✅ User fat model has all expected methods")
        else:
            print("ℹ️  No users found to test")
        
        print("\n🎉 All sync fat model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_fat_models():
    """Test async fat models against live API."""
    print("\n🔄 Testing Async Fat Models...")
    
    try:
        # Initialize async client (should read from environment)
        async with AsyncModeratelyAI() as client:
            print(f"✅ Async client initialized for team: {client.team_id}")
            
            # Test 1: List datasets (should return raw data)
            print("\n📊 Testing Async Datasets...")
            datasets_response = await client.datasets.list(page_size=1)
            print(f"✅ Listed datasets: {len(datasets_response.get('items', []))} items")
            
            # Test 2: If we have datasets, get one with rich functionality
            if datasets_response.get('items'):
                dataset_id = datasets_response['items'][0]['datasetId']
                dataset = await client.datasets.retrieve(dataset_id)
                print(f"✅ Retrieved dataset: {dataset.name} (ID: {dataset.dataset_id})")
                print(f"   - Record count: {dataset.record_count}")
                print(f"   - Processing status: {dataset.processing_status}")
                
                # Test async dataset methods exist
                assert hasattr(dataset, 'upload_data'), "Missing upload_data method"
                assert hasattr(dataset, 'download_data'), "Missing download_data method"
                assert hasattr(dataset, 'create_schema'), "Missing create_schema method"
                assert hasattr(dataset, 'schema_builder'), "Missing schema_builder method"
                print("✅ Async Dataset fat model has all expected methods")
            else:
                print("ℹ️  No datasets found to test")
            
            # Test 3: List files (should return raw data)
            print("\n📁 Testing Async Files...")
            files_response = await client.files.list(page_size=1)
            print(f"✅ Listed files: {len(files_response.get('items', []))} items")
            
            # Test 4: If we have files, get one with rich functionality
            if files_response.get('items'):
                file_id = files_response['items'][0].get('fileId') or files_response['items'][0].get('id')
                file = await client.files.retrieve(file_id)
                print(f"✅ Retrieved file: {file.name} (ID: {file.file_id})")
                print(f"   - Size: {file.file_size} bytes")
                print(f"   - MIME type: {file.mime_type}")
                print(f"   - Status: {file.status}")
                print(f"   - Is ready: {file.is_ready()}")
                print(f"   - Is document: {file.is_document()}")
                
                # Test async file methods exist
                assert hasattr(file, 'download'), "Missing download method"
                assert hasattr(file, 'delete'), "Missing delete method"
                print("✅ Async File fat model has all expected methods")
            else:
                print("ℹ️  No files found to test")
            
            # Test 5: List users (should return raw data)
            print("\n👥 Testing Async Users...")
            users_response = await client.users.list(page_size=1)
            print(f"✅ Listed users: {len(users_response.get('items', []))} items")
            
            # Test 6: If we have users, get one with rich functionality
            if users_response.get('items'):
                user_id = users_response['items'][0]['id']
                user = await client.users.retrieve(user_id)
                print(f"✅ Retrieved user: {user.display_name()} (ID: {user.user_id})")
                print(f"   - Email: {user.email}")
                print(f"   - Has name: {user.has_name()}")
                print(f"   - Is recent: {user.is_recent()}")
                
                # Test async user methods exist
                assert hasattr(user, 'update_profile'), "Missing update_profile method"
                assert hasattr(user, 'get_teams'), "Missing get_teams method"
                print("✅ Async User fat model has all expected methods")
            else:
                print("ℹ️  No users found to test")
            
            print("\n🎉 All async fat model tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all fat model tests."""
    print("🚀 Testing Fat Models Against Live API")
    print("=" * 50)
    
    # Test sync models
    sync_success = test_sync_fat_models()
    
    # Test async models
    async_success = asyncio.run(test_async_fat_models())
    
    print("\n" + "=" * 50)
    if sync_success and async_success:
        print("🎉 ALL TESTS PASSED! Fat models are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())