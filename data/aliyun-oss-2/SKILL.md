---
name: pywayne-aliyun-oss
description: Aliyun OSS (Object Storage Service) file management toolkit for Python. Use when working with Aliyun OSS to upload files, download files, list objects, delete files, manage directories, read file contents, check file existence, get file metadata, copy and move objects. Supports both authenticated (with API key/secret for write operations) and anonymous access (read-only).
---

# Pywayne Aliyun OSS

`pywayne.aliyun_oss.OssManager` provides a comprehensive toolkit for managing Aliyun OSS (Object Storage Service) buckets.

## Quick Start

```python
from pywayne.aliyun_oss import OssManager

# Initialize with write permissions
oss = OssManager(
    endpoint="https://oss-cn-xxx.aliyuncs.com",
    bucket_name="my-bucket",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Initialize with read-only (anonymous) access
oss = OssManager(
    endpoint="https://oss-cn-xxx.aliyuncs.com",
    bucket_name="my-bucket",
    verbose=False  # Disable verbose output
)
```

## Upload Operations

### Upload a local file

```python
oss.upload_file(key="data/sample.txt", file_path="./sample.txt")
```

### Upload text content

```python
oss.upload_text(key="config/settings.json", text='{"key": "value"}')
```

### Upload an image (numpy array)

```python
import cv2
image = cv2.imread("photo.jpg")
oss.upload_image(key="photos/photo.jpg", image=image)
```

### Upload entire directory

```python
oss.upload_directory(local_path="./local_folder", prefix="remote_folder/")
```

## Download Operations

### Download a single file

```python
# Preserve directory structure: downloads/data/sample.txt
oss.download_file(key="data/sample.txt", root_dir="./downloads")

# Use only basename: downloads/sample.txt
oss.download_file(key="data/sample.txt", root_dir="./downloads", use_basename=True)
```

### Download files with prefix

```python
oss.download_files_with_prefix(prefix="photos/", root_dir="./downloads")
```

### Download entire directory

```python
oss.download_directory(prefix="photos/", local_path="./downloads")
```

## List Operations

### List all keys in bucket

```python
keys = oss.list_all_keys()  # Returns sorted list
```

### List keys with prefix

```python
keys = oss.list_keys_with_prefix(prefix="data/")
```

### List directory contents (first level only)

```python
contents = oss.list_directory_contents(prefix="data/")
# Returns: [("file1.txt", False), ("subdir", True), ...]
```

## Read Operations

### Read file content as string

```python
content = oss.read_file_content(key="config/settings.json")
```

### Check if file exists

```python
if oss.key_exists("data/sample.txt"):
    print("File exists")
```

### Get file metadata

```python
metadata = oss.get_file_metadata("data/sample.txt")
# Returns: {'content_length': 1234, 'last_modified': ..., 'etag': ..., 'content_type': ...}
```

## Delete Operations

### Delete a single file

```python
oss.delete_file(key="data/sample.txt")
```

### Delete files with prefix

```python
oss.delete_files_with_prefix(prefix="temp/")
```

## Copy and Move Operations

### Copy object within bucket

```python
oss.copy_object(source_key="data/original.txt", target_key="backup/original.txt")
```

### Move object within bucket

```python
oss.move_object(source_key="data/temp.txt", target_key="archive/temp.txt")
```

## Important Notes

- **Write permissions**: Upload, delete, copy, and move operations require `api_key` and `api_secret`
- **Anonymous access**: Omit `api_key` and `api_secret` for read-only access
- **Directory handling**: OSS doesn't have real directories - use prefixes (keys ending with `/`)
- **Natural sorting**: `list_all_keys()` and `list_keys_with_prefix()` use natural sorting by default
- **Verbose output**: All methods print status messages when `verbose=True` (default)
