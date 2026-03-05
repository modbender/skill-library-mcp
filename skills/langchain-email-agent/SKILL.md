# EmailAgent README

## Overview

The `EmailAgent` class provides an AI-powered email composition and sending capability using LangChain with OpenAI's GPT model. It includes human-in-the-loop middleware that requires approval before emails are sent.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |

## Usage

```typescript
import { EmailAgent } from './email.agent';
import { SendEmailDto } from '../dto/send-email.dto';

const agent = new EmailAgent();

const dto: SendEmailDto = {
  email: 'recipient@example.com',
  name: 'John Doe',
  subject: 'Meeting Request',      // optional
  body: 'Initial email content',   // optional
  instructions: 'Keep it formal'   // optional
};

const result = await agent.sendEmail(dto);
```

## Human-in-the-Loop Middleware

The agent uses `humanInTheLoopMiddleware` which interrupts execution on the `EmailTool` before sending emails. This allows for:

- **approve** - Send the email as composed
- **edit** - Modify the email before sending
- **reject** - Cancel the email operation

The `readEmailTool` is excluded from interruption (`false`), allowing read operations to proceed without approval.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | Yes | Recipient email address |
| `name` | string | Yes | Recipient name |
| `subject` | string | No | Email subject line |
| `body` | string | No | Initial email body content |
| `instructions` | string | No | AI instructions for composing the email |

## Return Value

Returns the final message content from the agent as a string.
