# Pattern 10: Accessibility Checklist

## Problem / Context

Accessible applications ensure all users can interact with your interface, regardless of how they navigate (keyboard, screen reader, voice control). Accessibility is not a feature—it's a baseline requirement.

## When to Use

Always. Every component, every feature, every screen.

## When NOT to Use

Never skip accessibility.

## Core AntD Accessibility Features

Ant Design provides built-in accessibility for many components:

- **Form**: Automatic label association, error announcement
- **Modal**: Focus trap, ESC to close, focus return
- **Menu**: Arrow key navigation, aria-expanded
- **Table**: Sort button labels, row selection
- **Button**: Focus states, disabled states

## React Implementation Notes

### Focus Management

```tsx
import { useRef, useEffect } from 'react';

function FocusExample() {
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Focus on mount or when condition changes
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <Input ref={inputRef} />;
}
```

### Skip Links

```tsx
function SkipLinks() {
  return (
    <div className="skip-links">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#main-nav" className="skip-link">
        Skip to navigation
      </a>
    </div>
  );
}
```

### ARIA Labels

```tsx
// Icon-only buttons MUST have labels
<Button 
  icon={<DeleteOutlined />} 
  aria-label="Delete user"
/>

// Custom interactive elements
<div
  role="button"
  tabIndex={0}
  aria-pressed={isPressed}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Toggle
</div>
```

### Live Regions

```tsx
import { Alert } from 'antd';

// Status announcements
<div aria-live="polite" aria-atomic="true">
  {statusMessage && <Alert message={statusMessage} />}
</div>

// Important alerts
<div aria-live="assertive" aria-atomic="true">
  {errorMessage && <Alert type="error" message={errorMessage} />}
</div>
```

## Keyboard Navigation Checklist

| Feature | Implementation |
|---------|---------------|
| Tab order | Logical, top-to-bottom, left-to-right |
| Focus visible | Clear focus indicator (outline) |
| Escape key | Close modals, drawers, dropdowns |
| Enter/Space | Activate buttons, links, toggles |
| Arrow keys | Navigate within components (menu, tabs, radio) |
| Home/End | Jump to start/end of lists |
| Trap focus | Modal/dialog focus stays inside |
| Return focus | After modal closes, focus returns to trigger |

## Screen Reader Checklist

- [ ] All images have meaningful `alt` text
- [ ] Icon-only buttons have `aria-label`
- [ ] Form inputs have associated labels
- [ ] Required fields are marked (`aria-required` or `required`)
- [ ] Error messages linked via `aria-describedby`
- [ ] Page title updates on route change
- [ ] Dynamic content announced via live regions
- [ ] Tables have proper headers (`scope` or `headers`)

## Color & Contrast

- Minimum contrast ratio: **4.5:1** for normal text
- Minimum contrast ratio: **3:1** for large text (18px+)
- Don't rely on color alone to convey information
- Test with color blindness simulators

## Reduced Motion

```tsx
const prefersReducedMotion = 
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Disable animations for users who prefer reduced motion
const transition = prefersReducedMotion ? 'none' : 'all 0.3s';
```

## Accessibility Testing

### Automated Tools

- **axe DevTools**: Browser extension
- **Lighthouse**: Built into Chrome DevTools
- **ESLint plugin**: `eslint-plugin-jsx-a11y`

### Manual Testing

1. Keyboard-only navigation (no mouse)
2. Screen reader testing (NVDA, VoiceOver, JAWS)
3. Zoom to 200%, 400%
4. High contrast mode

## Do / Don't

| Do | Don't |
|----|-------|
| Test with keyboard only | Assume mouse users only |
| Provide visible focus indicators | Remove outlines with `outline: none` |
| Use semantic HTML | Replace buttons with divs |
| Write descriptive link text | Use "click here" links |
| Label all form inputs | Rely on placeholder text |
| Announce dynamic changes | Update content silently |

## Minimal Code Snippet

```tsx
import { useRef, useEffect, useState } from 'react';
import { 
  Button, Modal, Form, Input, Alert, 
  Switch, Select, Table, Space 
} from 'antd';

// Accessible Modal with focus management
export function AccessibleModal() {
  const [open, setOpen] = useState(false);
  const okButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (open) {
      // Focus first focusable element when modal opens
      setTimeout(() => okButtonRef.current?.focus(), 100);
    }
  }, [open]);

  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Modal</Button>
      
      <Modal
        title="Accessible Modal"
        open={open}
        onCancel={() => setOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setOpen(false)}>
            Cancel
          </Button>,
          <Button 
            key="ok" 
            type="primary" 
            ref={okButtonRef}
            onClick={() => setOpen(false)}
          >
            OK
          </Button>,
        ]}
        destroyOnClose
      >
        <p>This modal properly manages focus.</p>
      </Modal>
    </>
  );
}

// Accessible Form with error announcements
export function AccessibleForm() {
  const [form] = Form.useForm();
  const [error, setError] = useState<string | null>(null);
  const errorRef = useRef<HTMLDivElement>(null);

  const onFinish = (values: any) => {
    console.log(values);
    setError(null);
  };

  const onFinishFailed = () => {
    setError('Please fix the errors below');
    // Announce error to screen readers
    errorRef.current?.focus();
  };

  return (
    <Form
      form={form}
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      layout="vertical"
    >
      {error && (
        <div ref={errorRef} tabIndex={-1} aria-live="assertive">
          <Alert type="error" message={error} style={{ marginBottom: 16 }} />
        </div>
      )}

      <Form.Item
        label="Email"
        name="email"
        rules={[
          { required: true, message: 'Email is required' },
          { type: 'email', message: 'Enter a valid email' },
        ]}
      >
        <Input type="email" autoComplete="email" />
      </Form.Item>

      <Form.Item
        label="Role"
        name="role"
        rules={[{ required: true, message: 'Please select a role' }]}
      >
        <Select placeholder="Select role">
          <Select.Option value="admin">Administrator</Select.Option>
          <Select.Option value="user">User</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item name="newsletter" valuePropName="checked">
        <Switch aria-label="Subscribe to newsletter" />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">Submit</Button>
      </Form.Item>
    </Form>
  );
}
```
