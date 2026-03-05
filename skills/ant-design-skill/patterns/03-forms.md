# Pattern: Forms

## Problem / Context

Forms require validation, async submission handling, loading states, and error display. Without a consistent pattern, forms become inconsistent and error-prone across the application.

## When to Use

- Data entry interfaces
- Settings/configuration pages
- Authentication flows
- Search/filter panels

## When NOT to Use

- Simple single-field inputs (use standalone Input)
- Inline editing (use editable components)
- Real-time collaborative editing

## AntD Components Involved

- `Form` - Form container with validation
- `Form.Item` - Field wrapper with labels/errors
- `Input`, `Select`, `DatePicker` - Form controls
- `Button` - Submit actions
- `Alert` - Error summaries

## React Implementation Notes

### Form Instance Pattern

```tsx
const [form] = Form.useForm();
const [submitting, setSubmitting] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Async Submit Handler

```tsx
const handleSubmit = async (values: FormValues) => {
  setSubmitting(true);
  setError(null);
  
  try {
    await api.saveData(values);
    message.success('Saved successfully');
    form.resetFields();
  } catch (err) {
    setError(err.message);
    // Focus first error field
    form.scrollToField(Object.keys(err.fields)[0]);
  } finally {
    setSubmitting(false);
  }
};
```

### Field-Level Validation

```tsx
<Form.Item
  name="email"
  rules={[
    { required: true, message: 'Email is required' },
    { type: 'email', message: 'Invalid email format' },
  ]}
>
  <Input />
</Form.Item>
```

### Dynamic Disabled States

```tsx
<Form.Item shouldUpdate>
  {({ getFieldValue }) => {
    const type = getFieldValue('type');
    return (
      <Form.Item name="details">
        <Input disabled={type !== 'advanced'} />
      </Form.Item>
    );
  }}
</Form.Item>
```

## Accessibility / Keyboard

- Associate labels with inputs via `htmlFor`
- Error messages linked via `aria-describedby`
- Focus management on validation errors
- Logical tab order

## Do / Don't

**Do:**
- Validate on blur for immediate feedback
- Show loading state on submit button
- Group related fields visually
- Use clear, actionable error messages

**Don't:**
- Validate aggressively on every keystroke
- Show empty error messages
- Disable entire form during submit
- Mix controlled and uncontrolled inputs

## Minimal Code Snippet

```tsx
import { Form, Input, Button, Alert, message } from 'antd';
import { useState } from 'react';

function UserForm() {
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFinish = async (values: any) => {
    setSubmitting(true);
    try {
      await fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(values),
      });
      message.success('User created');
      form.resetFields();
    } catch (err) {
      setError('Failed to create user');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      {error && (
        <Alert message={error} type="error" style={{ marginBottom: 16 }} />
      )}
      <Form.Item
        name="name"
        label="Name"
        rules={[{ required: true }]}
      >
        <Input />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={submitting}>
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
}
```
