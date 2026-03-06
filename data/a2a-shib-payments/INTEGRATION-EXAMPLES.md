# Integration Examples

This document shows how to integrate the A2A SHIB Payment Agent with popular AI agent frameworks.

---

## 🦜 LangChain Integration

### Python Example

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import requests

# A2A Payment Tool
def call_payment_agent(query: str) -> str:
    """Send a message to the A2A SHIB payment agent"""
    response = requests.post(
        "http://localhost:8003/a2a/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "messageId": "langchain-1",
                    "role": "user",
                    "parts": [{"kind": "text", "text": query}]
                }
            },
            "id": 1
        }
    )
    return response.json()["result"]["parts"][0]["text"]

payment_tool = Tool(
    name="A2A_Payment_Agent",
    func=call_payment_agent,
    description="Send SHIB payments, create escrows, negotiate prices, check reputation"
)

# Create LangChain agent with payment capability
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, [payment_tool], system_message)
agent_executor = AgentExecutor(agent=agent, tools=[payment_tool])

# Use it
result = agent_executor.invoke({"input": "Check my SHIB balance"})
print(result["output"])

result = agent_executor.invoke({
    "input": "Create an escrow for 500 SHIB to pay data-agent for market data"
})
print(result["output"])
```

### JavaScript/TypeScript Example

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";
import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";

// A2A Payment Tool
const paymentTool = new DynamicStructuredTool({
  name: "a2a_payment_agent",
  description: "Send SHIB payments, create escrows, negotiate prices, check reputation",
  schema: z.object({
    query: z.string().describe("The payment-related query or command"),
  }),
  func: async ({ query }) => {
    const response = await fetch("http://localhost:8003/a2a/jsonrpc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "message/send",
        params: {
          message: {
            kind: "message",
            messageId: "langchain-1",
            role: "user",
            parts: [{ kind: "text", text: query }]
          }
        },
        id: 1
      })
    });
    const data = await response.json();
    return data.result.parts[0].text;
  }
});

// Create agent
const model = new ChatOpenAI({ modelName: "gpt-4" });
const agent = await createOpenAIFunctionsAgent({
  llm: model,
  tools: [paymentTool],
  prompt: systemPrompt
});

const executor = new AgentExecutor({ agent, tools: [paymentTool] });

// Use it
const result = await executor.invoke({
  input: "Create an escrow for 500 SHIB to pay data-agent"
});
console.log(result.output);
```

---

## ☁️ AWS Bedrock Agents Integration

### Agent Action Group Configuration

```json
{
  "actionGroupName": "SHIBPaymentActions",
  "description": "SHIB payment, escrow, and reputation actions",
  "actionGroupExecutor": {
    "lambda": "arn:aws:lambda:us-east-1:123456789012:function:a2a-payment-proxy"
  },
  "apiSchema": {
    "payload": "..."
  }
}
```

### Lambda Proxy Function (Node.js)

```javascript
const fetch = require('node-fetch');

exports.handler = async (event) => {
  const { apiPath, requestBody } = event;
  
  // Map Bedrock action to A2A command
  let command = '';
  switch (apiPath) {
    case '/payment/send':
      command = `send ${requestBody.amount} SHIB to ${requestBody.recipient}`;
      break;
    case '/escrow/create':
      command = `escrow create ${requestBody.amount} SHIB for ${requestBody.purpose} payee ${requestBody.payee}`;
      break;
    case '/reputation/check':
      command = `reputation check ${requestBody.agentId}`;
      break;
    default:
      return { statusCode: 400, body: 'Unknown action' };
  }

  // Call A2A agent
  const response = await fetch('http://your-agent:8003/a2a/jsonrpc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'message/send',
      params: {
        message: {
          kind: 'message',
          messageId: event.messageId,
          role: 'user',
          parts: [{ kind: 'text', text: command }]
        }
      },
      id: 1
    })
  });

  const data = await response.json();
  
  return {
    statusCode: 200,
    body: {
      messageVersion: '1.0',
      response: {
        actionGroup: event.actionGroup,
        apiPath: event.apiPath,
        httpMethod: event.httpMethod,
        httpStatusCode: 200,
        responseBody: {
          'application/json': {
            body: data.result.parts[0].text
          }
        }
      }
    }
  };
};
```

### OpenAPI Schema for Bedrock

```yaml
openapi: 3.0.0
info:
  title: A2A SHIB Payment API
  version: 1.0.0
paths:
  /payment/send:
    post:
      summary: Send SHIB payment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                amount:
                  type: number
                recipient:
                  type: string
      responses:
        '200':
          description: Payment sent
  /escrow/create:
    post:
      summary: Create escrow
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                amount:
                  type: number
                purpose:
                  type: string
                payee:
                  type: string
      responses:
        '200':
          description: Escrow created
  /reputation/check:
    post:
      summary: Check agent reputation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                agentId:
                  type: string
      responses:
        '200':
          description: Reputation data
```

---

## 🦪 OpenClaw Integration

### As a Skill

The agent can be used as a standalone OpenClaw skill:

```bash
# Install in OpenClaw skills directory
cd ~/clawd/skills
git clone https://github.com/marcus20232023/a2a-shib-payments.git shib-payments
cd shib-payments
npm install

# Configure
cp .env.example .env.local
nano .env.local  # Add wallet details

# Start
node a2a-agent-full.js
```

### SKILL.md Example

```markdown
# SKILL.md - SHIB Payment Agent

## Description
A2A protocol payment agent for SHIB on Polygon. Provides escrow, negotiation, and reputation services.

## Usage
The agent runs on port 8003. OpenClaw can communicate via A2A protocol.

## Commands
- `send [amount] SHIB to [address]` - Send payment
- `balance` - Check SHIB balance
- `escrow create [amount] SHIB for [purpose] payee [agent]` - Create escrow
- `reputation check [agentId]` - Check agent reputation

## Configuration
Set in `.env.local`:
- WALLET_PRIVATE_KEY
- RPC_URL (Polygon)
- SHIB_CONTRACT_ADDRESS

## Port
8003 (default)
```

---

## 🤖 AutoGen Integration

### Multi-Agent Setup

```python
import autogen
import requests

# A2A Payment Proxy Agent
payment_proxy = autogen.AssistantAgent(
    name="PaymentProxy",
    llm_config={"config_list": config_list},
    system_message="You handle payments via the A2A SHIB payment system."
)

def call_a2a_agent(message: str) -> str:
    response = requests.post(
        "http://localhost:8003/a2a/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "messageId": "autogen-1",
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}]
                }
            },
            "id": 1
        }
    )
    return response.json()["result"]["parts"][0]["text"]

# Register A2A function
autogen.register_function(
    call_a2a_agent,
    caller=payment_proxy,
    executor=user_proxy,
    name="a2a_payment",
    description="Send SHIB payments, create escrows, check reputation"
)

# Use in conversation
user_proxy.initiate_chat(
    payment_proxy,
    message="Create an escrow for 500 SHIB to buy market data from data-agent"
)
```

---

## 🌐 Direct A2A Protocol Integration

### REST API

```bash
# Send message via REST
curl -X POST http://localhost:8003/a2a/rest/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "kind": "message",
      "messageId": "rest-1",
      "role": "user",
      "parts": [{"kind": "text", "text": "balance"}]
    }
  }'
```

### JSON-RPC

```javascript
const response = await fetch('http://localhost:8003/a2a/jsonrpc', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'message/send',
    params: {
      message: {
        kind: 'message',
        messageId: 'custom-1',
        role: 'user',
        parts: [{ kind: 'text', text: 'send 100 SHIB to 0x...' }]
      }
    },
    id: 1
  })
});

const data = await response.json();
console.log(data.result);
```

### Agent Discovery

```javascript
// Discover payment agent via A2A registry
const response = await fetch('http://localhost:8003/.well-known/agent-card.json');
const agentCard = await response.json();

console.log(agentCard.name);         // "SHIB Payment Agent"
console.log(agentCard.capabilities); // Payment, escrow, negotiation, reputation
console.log(agentCard.endpoints);    // A2A endpoints
```

---

## 📦 Docker Integration

### Docker Compose Multi-Agent Setup

```yaml
version: '3.8'
services:
  payment-agent:
    image: node:18
    working_dir: /app
    volumes:
      - ./a2a-shib-payments:/app
    environment:
      - WALLET_PRIVATE_KEY=${WALLET_PRIVATE_KEY}
      - RPC_URL=https://polygon-rpc.com
    command: npm start
    ports:
      - "8003:8003"
    networks:
      - agent-network

  langchain-agent:
    image: python:3.11
    working_dir: /app
    volumes:
      - ./langchain-agent:/app
    environment:
      - A2A_PAYMENT_URL=http://payment-agent:8003
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: python agent.py
    networks:
      - agent-network
    depends_on:
      - payment-agent

networks:
  agent-network:
    driver: bridge
```

---

## 🔒 Production Best Practices

### 1. Authentication

```javascript
// Add API key authentication
const response = await fetch('http://localhost:8003/a2a/jsonrpc', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.A2A_API_KEY
  },
  body: JSON.stringify({...})
});
```

### 2. Error Handling

```python
def safe_a2a_call(query: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8003/a2a/jsonrpc",
                json={...},
                timeout=10
            )
            response.raise_for_status()
            return response.json()["result"]["parts"][0]["text"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Rate Limiting

```javascript
// Respect rate limits (10 req/min by default)
import { RateLimiter } from 'limiter';

const limiter = new RateLimiter({
  tokensPerInterval: 10,
  interval: 'minute'
});

await limiter.removeTokens(1);
const result = await callA2AAgent(query);
```

---

## 📚 Additional Resources

- **A2A Protocol Spec:** https://a2a-protocol.org
- **Main Documentation:** [README.md](README.md)
- **API Reference:** [ESCROW-NEGOTIATION-GUIDE.md](ESCROW-NEGOTIATION-GUIDE.md)
- **Security Guide:** [PRODUCTION-HARDENING.md](PRODUCTION-HARDENING.md)
- **Deployment Options:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🤝 Community Examples

Have an integration example for another framework? Submit a PR!

**Wanted:**
- CrewAI integration
- Semantic Kernel integration
- LlamaIndex integration
- Haystack integration

**Contributors:**
- *(Your name here!)*
