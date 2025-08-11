# File Operations Example

This example demonstrates the complete file operations workflow using the Moderately AI Python SDK, showing the exact method mappings from REST API endpoints to SDK methods.

## What This Example Shows

- **Complete file lifecycle**: Upload → List → Download → Delete
- **REST API to SDK method mappings**
- **Both FileModel and resource-level approaches**
- **Rich file type detection and properties**
- **Proper error handling patterns**

## REST API vs SDK Method Mapping

| Operation | REST API | SDK Method |
|-----------|----------|------------|
| **Upload** | `POST /files/upload-url` + `PUT presigned-url` + `POST /files/{id}/complete` | `client.files.upload(file_path)` |
| **List** | `GET /files?teamIds={team_id}` | `client.files.list()` |
| **Download** | `GET /files/{id}/download` | `file.download()` or `client.files.download(file_id)` |
| **Delete** | `DELETE /files/{id}` | `file.delete()` or `client.files.delete(file_id)` |

## Key Features Demonstrated

### 1. File Upload
- Automatic presigned URL workflow (handled internally)
- MIME type detection
- File metadata support
- Returns `FileModel` instance with rich methods

### 2. File Listing
- Team-scoped filtering (automatic)
- Pagination support
- Results returned as `FileModel` instances
- Rich filtering options (status, MIME type, etc.)

### 3. File Download
- **Method 1**: Using `FileModel.download()` - Download to disk or memory
- **Method 2**: Using `client.files.download()` - Resource-level approach
- Automatic presigned URL handling

### 4. File Properties & Rich Methods
- File type detection: `is_csv()`, `is_document()`, `is_image()`, `is_text()`
- Status checking: `is_ready()`, `is_processing()`, `has_error()`
- Properties: `file_id`, `name`, `file_size`, `mime_type`, etc.

### 5. File Deletion
- Using `FileModel.delete()` method
- Permanent deletion (cannot be undone)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   - `MODERATELY_API_KEY=your_api_key`
   - `MODERATELY_TEAM_ID=your_team_id`

## Running the Examples

### Synchronous Version
From the repository root:
```bash
dotenvx run -- python python/examples/01-file-operations/main.py
```

### Asynchronous Version  
From the repository root:
```bash
dotenvx run -- python python/examples/01-file-operations/main_async.py
```

## Expected Output

```
🚀 File Operations Example - Moderately AI SDK
============================================================

1️⃣ Initializing SDK Client...
✅ Client initialized for team: your_team_id
✅ Created sample file: sample_data.txt (281 bytes)

2️⃣ Uploading File...
✅ File uploaded successfully!
   File ID: abc123...
   Name: Sample Data File.txt
   Status: completed

3️⃣ Listing Files...
✅ Found 5 files (page 1 of 3):
   ✅ Sample Data File.txt (281 bytes)
   ✅ Other File.csv [CSV] (1024 bytes)

4️⃣ Downloading File (Method 1: FileModel)...
✅ File downloaded to: downloaded_sample.txt
✅ Content verification: Files match perfectly!

5️⃣ Downloading File (Method 2: Client Resource)...
✅ File downloaded to memory: 281 bytes

6️⃣ File Information & Rich Methods...
   Extension: .txt
   Is Text: True
   Is CSV: False
   Is Ready: True

7️⃣ Deleting File...
✅ File deleted successfully!

🎉 File operations completed successfully!
```

## Error Handling

The example demonstrates proper error handling for:
- Missing environment variables
- Authentication errors
- API errors during operations
- File not found scenarios

## File Structure

```
01-file-operations/
├── README.md           # This file  
├── main.py            # Synchronous example script
├── main_async.py      # Asynchronous example script
└── requirements.txt   # Dependencies
```

## Next Steps

This example provides the foundation for file operations. For more advanced use cases, consider:
- Bulk file operations
- File metadata management
- Integration with datasets
- Async file operations with `AsyncModeratelyAI`

## Customer Questions Answered

**Q: Do you provide a native async client/class?**  
A: Yes! Use `AsyncModeratelyAI` with the same interface (all methods are `async`). See `main_async.py` for a complete example.

**Q: For upload do we have to do the pre-signed URL or there is direct upload?**  
A: Direct upload! `client.files.upload()` handles the entire presigned URL workflow internally.

**Q: Exact SDK methods for our flow?**  
A: See the mapping table above - single method calls replace multi-step REST workflows.

**Q: How to set team scoping and base URL per environment?**  
A: Via constructor parameters or environment variables. Team scoping is automatic once set.