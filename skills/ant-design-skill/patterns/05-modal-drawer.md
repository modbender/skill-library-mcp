# Pattern: Modal / Drawer

## Problem / Context

Modals and drawers are used for focused tasks, confirmations, and detail views. Poor implementation leads to focus traps, scroll issues, and inconsistent closing behavior.

## When to Use

- **Modal**: Critical confirmations, small forms, alert dialogs
- **Drawer**: Side panels for detailed editing, filters, navigation

## When NOT to Use

- **Modal**: Large forms (use Drawer or page)
- **Drawer**: Simple confirmations (overkill)
- Both: Nested modals/drawers (reconsider UX)

## AntD Components Involved

- `Modal` - Centered overlay dialogs
- `Drawer` - Side panels
- `Form` - Often used inside both
- `Button` - Action buttons

## React Implementation Notes

### Controlled Visibility Pattern

```tsx
const [open, setOpen] = useState(false);
const [confirmLoading, setConfirmLoading] = useState(false);

const showModal = () => setOpen(true);
const handleCancel = () => setOpen(false);
```

### Async Confirmation Handler

```tsx
const handleOk = async () => {
  setConfirmLoading(true);
  try {
    await api.deleteItem(id);
    message.success('Deleted');
    setOpen(false);
  } finally {
    setConfirmLoading(false);
  }
};
```

### Form Inside Modal

```tsx
const [form] = Form.useForm();

<Modal
  open={open}
  onOk={() => form.submit()}
  confirmLoading={confirmLoading}
>
  <Form form={form} onFinish={handleSubmit}>
    <Form.Item name="name" rules={[{ required: true }]}>
      <Input />
    </Form.Item>
  </Form>
</Modal>
```

### Drawer for Side Panels

```tsx
<Drawer
  title="Edit User"
  open={open}
  onClose={() => setOpen(false)}
  width={520}
  extra={
    <Space>
      <Button onClick={() => setOpen(false)}>Cancel</Button>
      <Button type="primary" onClick={handleSave}>Save</Button>
    </Space>
  }
>
  <Form layout="vertical">
    {/* Form fields */}
  </Form>
</Drawer>
```

## Accessibility / Keyboard

- Focus trapped inside modal when open
- Escape key closes modal
- Return focus to trigger on close
- Proper aria-labels on buttons

## Do / Don't

**Do:**
- Use consistent widths (Modal: 520px standard)
- Show loading state during async operations
- Clear form on close for create modals
- Use `destroyOnClose` for memory cleanup

**Don't:**
- Stack multiple modals
- Disable backdrop click to close (unless critical)
- Show modal on page load without user action
- Forget to handle loading states

## Minimal Code Snippet

```tsx
import { Modal, Button, Form, Input, message } from 'antd';
import { useState } from 'react';

function ConfirmModal() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleOk = async () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setOpen(false);
      message.success('Confirmed');
    }, 2000);
  };

  return (
    <>
      <Button type="primary" onClick={() => setOpen(true)}>
        Open Modal
      </Button>
      <Modal
        title="Confirm Action"
        open={open}
        onOk={handleOk}
        confirmLoading={loading}
        onCancel={() => setOpen(false)}
      >
        Are you sure you want to proceed?
      </Modal>
    </>
  );
}
```
