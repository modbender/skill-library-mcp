# Pattern: Notifications

## Problem / Context

Notifications need to be contextual, non-blocking, and actionable. Poor notification patterns overwhelm users or provide useless information without next steps.

## When to Use

- Action completion feedback
- Error messages with recovery options
- Async process updates
- System alerts

## When NOT to Use

- Primary information (use Alert in page)
- Blocking errors (use Modal)
- Validation messages (use Form.Item)

## AntD Components Involved

- `message` - Brief toast notifications
- `notification` - Rich notifications with actions
- `Alert` - Inline banners (page-level)
- `Badge` - Indicators on icons

## React Implementation Notes

### Message Pattern

```tsx
import { message } from 'antd';

// Success
message.success('Saved successfully');

// Error with duration
message.error('Failed to save', 5);

// Loading then resolve
const hide = message.loading('Saving...', 0);
await api.save();
hide();
message.success('Saved!');
```

### Notification Pattern

```tsx
import { notification } from 'antd';

notification.success({
  message: 'Export Complete',
  description: 'Your report is ready for download.',
  btn: (
    <Button type="primary" onClick={handleDownload}>
      Download
    </Button>
  ),
  duration: 0, // Don't auto-close
});
```

### Error Handling Pattern

```tsx
const handleError = (error: Error) => {
  if (error.response?.status === 401) {
    notification.error({
      message: 'Session Expired',
      description: 'Please log in again.',
      btn: <Button onClick={() => navigate('/login')}>Login</Button>,
    });
  } else {
    message.error(error.message || 'An error occurred');
  }
};
```

### Global Error Boundary

```tsx
class ErrorBoundary extends React.Component {
  componentDidCatch(error) {
    notification.error({
      message: 'Something went wrong',
      description: error.message,
    });
  }
}
```

## Accessibility / Keyboard

- Notifications auto-dismiss with sufficient time (4-6s)
- Pause on hover for reading
- Keyboard accessible close buttons
- Screen reader announcements

## Do / Don't

**Do:**
- Keep messages concise (max 2 lines)
- Use appropriate notification type
- Provide action buttons for important notifications
- Group related notifications

**Don't:**
- Show multiple identical notifications
- Use notifications for form validation
- Auto-dismiss critical errors
- Block user actions with notifications

## Minimal Code Snippet

```tsx
import { message, notification, Button } from 'antd';

function NotificationDemo() {
  const showSuccess = () => {
    message.success('Operation completed');
  };

  const showNotification = () => {
    notification.info({
      message: 'New Message',
      description: 'You have a new notification.',
      btn: (
        <Button size="small" onClick={() => console.log('View')}>
          View
        </Button>
      ),
    });
  };

  return (
    <>
      <Button onClick={showSuccess}>Show Message</Button>
      <Button onClick={showNotification}>Show Notification</Button>
    </>
  );
}
```
