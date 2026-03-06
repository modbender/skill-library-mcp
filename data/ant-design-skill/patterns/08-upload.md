# Pattern: Upload

## Problem / Context

File uploads need progress indication, validation, error handling, and preview capabilities. Poor upload UX leaves users wondering if their file was received.

## When to Use

- Document uploads
- Image/file attachments
- Bulk file imports
- Avatar/profile picture updates

## When NOT to Use

- Simple text input (use Input.TextArea)
- Drag-drop zones for single small files (overkill)
- Direct camera capture (use specialized components)

## AntD Components Involved

- `Upload` - File upload component
- `Progress` - Upload progress indicator
- `Modal` - Image preview
- `Button` - Upload trigger
- `message` - Upload status feedback

## React Implementation Notes

### Basic Upload Pattern

```tsx
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

<Upload
  action="/api/upload"
  onChange={({ file }) => {
    if (file.status === 'done') {
      message.success(`${file.name} uploaded successfully`);
    } else if (file.status === 'error') {
      message.error(`${file.name} upload failed`);
    }
  }}
>
  <Button icon={<UploadOutlined />}>Click to Upload</Button>
</Upload>
```

### Controlled Upload with Preview

```tsx
const [fileList, setFileList] = useState<UploadFile[]>([]);
const [previewOpen, setPreviewOpen] = useState(false);
const [previewImage, setPreviewImage] = useState('');

const handlePreview = async (file: UploadFile) => {
  setPreviewImage(file.url || file.thumbUrl);
  setPreviewOpen(true);
};

const beforeUpload = (file: File) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('You can only upload JPG/PNG files!');
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('Image must be smaller than 2MB!');
  }
  return isJpgOrPng && isLt2M;
};

<Upload
  listType="picture-card"
  fileList={fileList}
  onPreview={handlePreview}
  onChange={({ fileList }) => setFileList(fileList)}
  beforeUpload={beforeUpload}
>
  {fileList.length >= 8 ? null : '+ Upload'}
</Upload>
```

### Drag and Drop Upload

```tsx
import { InboxOutlined } from '@ant-design/icons';

const { Dragger } = Upload;

<Dragger
  name="file"
  multiple
  action="/api/upload"
  onChange={handleChange}
>
  <p className="ant-upload-drag-icon">
    <InboxOutlined />
  </p>
  <p className="ant-upload-text">
    Click or drag file to this area
  </p>
</Dragger>
```

## Accessibility / Keyboard

- Upload button is focusable
- Keyboard triggers file picker (Space/Enter)
- Progress announced to screen readers
- Error messages are descriptive

## Do / Don't

**Do:**
- Validate file type and size before upload
- Show clear progress indication
- Allow multiple file selection when appropriate
- Provide preview for images

**Don't:**
- Accept all file types without validation
- Show upload without progress
- Block the UI during upload
- Forget error handling

## Minimal Code Snippet

```tsx
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useState } from 'react';

function FileUpload() {
  const [fileList, setFileList] = useState([]);

  const props = {
    beforeUpload: (file) => {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('File must be smaller than 2MB!');
      }
      return isLt2M;
    },
    onChange: ({ file, fileList }) => {
      if (file.status === 'done') {
        message.success(`${file.name} uploaded`);
      }
      setFileList(fileList);
    },
  };

  return (
    <Upload {...props} fileList={fileList}>
      <Button icon={<UploadOutlined />}>Upload</Button>
    </Upload>
  );
}
```
