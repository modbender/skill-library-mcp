# Shopify Files

Manage file uploads, images, videos, and media library via the GraphQL Admin API.

## Overview

Files represent digital assets including images, videos, 3D models, and documents uploaded to the store.

## List Files

```graphql
query ListFiles($first: Int!, $after: String, $query: String) {
  files(first: $first, after: $after, query: $query, sortKey: CREATED_AT, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      alt
      createdAt
      fileStatus
      ... on MediaImage {
        image {
          url
          width
          height
        }
        mimeType
      }
      ... on Video {
        sources {
          url
          mimeType
        }
      }
      ... on GenericFile {
        url
        mimeType
      }
    }
  }
}
```
Variables: `{ "first": 20 }`

## Upload Files (Two-Step Process)

### Step 1: Create Staged Upload

```graphql
mutation CreateStagedUpload($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets {
      url
      resourceUrl
      parameters {
        name
        value
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "input": [
    {
      "filename": "product-image.jpg",
      "mimeType": "image/jpeg",
      "httpMethod": "POST",
      "resource": "FILE"
    }
  ]
}
```

### Step 2: Create File from Staged Upload

```graphql
mutation CreateFile($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      id
      alt
      fileStatus
      ... on MediaImage {
        image {
          url
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "files": [
    {
      "alt": "Summer collection product",
      "contentType": "IMAGE",
      "originalSource": "https://storage.shopify.com/staged/abc123..."
    }
  ]
}
```

## Create File from URL

```graphql
mutation CreateFileFromUrl($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      id
      alt
      fileStatus
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "files": [
    {
      "alt": "Product image",
      "contentType": "IMAGE",
      "originalSource": "https://example.com/images/product.jpg"
    }
  ]
}
```

## Create Video

```graphql
mutation CreateVideo($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      id
      fileStatus
      ... on Video {
        sources {
          url
          mimeType
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "files": [
    {
      "alt": "Product demo video",
      "contentType": "VIDEO",
      "originalSource": "https://storage.shopify.com/staged/video123..."
    }
  ]
}
```

## Create External Video (YouTube/Vimeo)

```graphql
mutation CreateExternalVideo($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      id
      ... on ExternalVideo {
        embedUrl
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "files": [
    {
      "alt": "Product tutorial",
      "contentType": "EXTERNAL_VIDEO",
      "originalSource": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
```

## Update File

```graphql
mutation UpdateFile($files: [FileUpdateInput!]!) {
  fileUpdate(files: $files) {
    files {
      id
      alt
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "files": [
    {
      "id": "gid://shopify/MediaImage/123",
      "alt": "Updated alt text for accessibility"
    }
  ]
}
```

## Delete Files

```graphql
mutation DeleteFiles($fileIds: [ID!]!) {
  fileDelete(fileIds: $fileIds) {
    deletedFileIds
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "fileIds": ["gid://shopify/MediaImage/123", "gid://shopify/MediaImage/456"]
}
```

## File Content Types

| Type | Description |
|------|-------------|
| `IMAGE` | JPEG, PNG, GIF, WebP images |
| `VIDEO` | MP4, WebM videos |
| `EXTERNAL_VIDEO` | YouTube, Vimeo embeds |
| `MODEL_3D` | 3D model files (GLB, USDZ) |
| `FILE` | Generic files (PDF, documents) |

## File Status

| Status | Description |
|--------|-------------|
| `UPLOADED` | File uploaded, processing |
| `PROCESSING` | Being processed |
| `READY` | Ready for use |
| `FAILED` | Upload/processing failed |

## Query Files by Type

```graphql
query ListImages($first: Int!) {
  files(first: $first, query: "media_type:IMAGE") {
    nodes {
      id
      ... on MediaImage {
        image {
          url
          width
          height
        }
      }
    }
  }
}
```

## Search Files

```graphql
query SearchFiles($query: String!) {
  files(first: 10, query: $query) {
    nodes {
      id
      alt
      fileStatus
    }
  }
}
```
Variables: `{ "query": "alt:product OR filename:banner" }`

## File Search Filters

| Filter | Example | Description |
|--------|---------|-------------|
| `media_type` | `media_type:IMAGE` | Filter by type |
| `status` | `status:READY` | Filter by status |
| `filename` | `filename:hero` | Search filename |
| `alt` | `alt:product` | Search alt text |
| `created_at` | `created_at:>2024-01-01` | Filter by date |

## Staged Upload Resources

| Resource | Description |
|----------|-------------|
| `FILE` | General file upload |
| `IMAGE` | Image file |
| `VIDEO` | Video file |
| `MODEL_3D` | 3D model file |
| `BULK_MUTATION_VARIABLES` | Bulk operation data |
| `PRODUCT_MEDIA` | Product media attachment |

## Staged Upload HTTP Methods

| Method | Use Case |
|--------|----------|
| `POST` | Multipart form upload |
| `PUT` | Direct binary upload |

## API Scopes Required

- `read_files` - Read files
- `write_files` - Upload, update, delete files

## Notes

- Files are processed asynchronously; poll `fileStatus` until `READY`
- Maximum of 250 files per `fileCreate` call
- Alt text improves SEO and accessibility
- Use staged uploads for large files
- External videos don't count against file storage
- 3D models require GLB or USDZ format
