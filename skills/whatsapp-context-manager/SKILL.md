---
name: WhatsApp Intelligent Context Manager - Skill Guide
description: This skill provides an AI-powered context management system for
  WhatsApp customer service agents, enabling instant access to customer history,
  sentiment analysis, and smart response suggestions.
---

# WhatsApp Intelligent Context Manager - Skill Guide

This skill provides an AI-powered context management system for WhatsApp customer service agents, enabling instant access to customer history, sentiment analysis, and smart response suggestions.

## Quick Installation

```bash
# Download and extract
unzip whatsapp-context-manager.zip
cd whatsapp-context-manager

# Verify installation (no dependencies needed!)
python install_check_whatsapp.py

# Run tests
python test_whatsapp.py

# Try examples
python examples_whatsapp.py
```

## What Problem Does This Solve?

**Without This System:**
- ❌ Agents have no context when customer messages arrive
- ❌ No idea if customer is VIP or first-timer
- ❌ Can't see order status without switching systems
- ❌ Don't know if message is urgent or can wait
- ❌ Guessing what to say instead of smart suggestions

**With This System:**
- ✅ Complete customer context in 2 seconds
- ✅ Automatic sentiment analysis (angry/happy/neutral)
- ✅ Smart priority (critical/high/normal/low)
- ✅ Order status right there
- ✅ AI-powered response suggestions
- ✅ VIP customer detection

## Basic Usage

### 1. Initialize the System

```python
from whatsapp_context_manager import ContextManager

# Create context manager (creates local database)
manager = ContextManager("production.db")
```

### 2. Process Incoming WhatsApp Message

```python
# When a WhatsApp message arrives
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="Where is my order?!",
    agent_id="agent_001"
)
```

### 3. Display Context to Agent

```python
# Show agent what they need to know
print(f"Priority: {context.priority.value}")        # "critical"
print(f"Sentiment: {context.sentiment.value}")      # "negative"
print(f"Category: {context.category}")              # "order_status"
print(f"VIP Customer: {context.customer.is_vip}")   # True/False

# Key insights
for insight in context.key_insights:
    print(f"💡 {insight}")

# Warnings
for warning in context.warnings:
    print(f"⚠️ {warning}")

# Suggested responses
for response in context.suggested_responses:
    print(f"💬 {response}")
```

### 4. Send Reply

```python
# Agent sends reply
manager.send_message(
    phone="+1234567890",
    message_content="Your order #12345 is on the way!",
    agent_id="agent_001"
)
```

## What Agent Sees - Dashboard Example

```
┌──────────────────────────────────────────────────────┐
│                  AGENT DASHBOARD                     │
├──────────────────────────────────────────────────────┤
│ Customer: +1234567890                                │
│ Name: John Doe                                       │
│ VIP: YES                                             │
├──────────────────────────────────────────────────────┤
│ Priority: CRITICAL                                   │
│ Sentiment: NEGATIVE                                  │
│ Category: ORDER_STATUS                               │
├──────────────────────────────────────────────────────┤
│ KEY INSIGHTS:                                        │
│   • 🌟 VIP Customer - Prioritize response            │
│   • 📦 Active Order: #ORD-12345 - shipped            │
│   • 🚚 Tracking: TRK-ABC123                          │
│   • ⚡ Customer expects fast replies (~2min)         │
├──────────────────────────────────────────────────────┤
│ WARNINGS:                                            │
│   • 🚨 CRITICAL: Requires immediate attention!       │
│   • 😡 Customer is very upset - handle with care     │
├──────────────────────────────────────────────────────┤
│ SUGGESTED RESPONSES:                                 │
│   1. Let me check your order status right away.     │
│   2. Your order #ORD-12345 is shipped.               │
└──────────────────────────────────────────────────────┘
```

## Core Features

### 1. Automatic Sentiment Analysis

Detects customer mood from message:

```python
# System automatically analyzes sentiment
context = manager.process_incoming_message(phone, "This is TERRIBLE!", agent_id)
print(context.sentiment.value)  # "very_negative"

context = manager.process_incoming_message(phone, "Thanks!", agent_id)
print(context.sentiment.value)  # "positive"
```

**Sentiment Levels:**
- 😡 `very_negative` - Angry, furious, scam
- 😟 `negative` - Disappointed, problem
- 😐 `neutral` - Questions, info requests
- 😊 `positive` - Thanks, happy
- 🤩 `very_positive` - Excellent, love it

### 2. Message Categorization

Automatically categorizes messages:

```python
# System automatically categorizes
context = manager.process_incoming_message(phone, "Where is my package?", agent_id)
print(context.category)  # MessageCategory.ORDER_STATUS

context = manager.process_incoming_message(phone, "Refund please!", agent_id)
print(context.category)  # MessageCategory.PAYMENT
```

**Categories:**
- 📦 `ORDER_STATUS` - Delivery, tracking, shipment
- 💳 `PAYMENT` - Refund, billing, transaction
- 🔴 `COMPLAINT` - Problem, issue, broken
- 🛍️ `PRODUCT_INQUIRY` - Price, stock, features
- 🆘 `SUPPORT` - Help, how-to, questions
- 💰 `SALES` - Buy, purchase, interested
- ⭐ `FEEDBACK` - Review, opinion
- ❓ `OTHER` - Uncategorized

### 3. Priority Calculation

Smart priority based on multiple factors:

```python
# System calculates priority
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="My payment failed!!!",
    agent_id="agent_001"
)
print(context.priority.value)  # "critical"
```

**Priority Levels:**
- 🔴 `CRITICAL` - Angry customer, payment issue, VIP unhappy
- 🟠 `HIGH` - Complaints, negative sentiment
- 🟡 `NORMAL` - General questions
- 🟢 `LOW` - Info requests, positive feedback

### 4. Response Suggestions

AI suggests appropriate responses:

```python
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="When will my order arrive?",
    agent_id="agent_001"
)

# Get suggestions
for response in context.suggested_responses:
    print(response)
# Output:
# "Let me check your order status right away."
# "Your order #12345 is currently shipped."
# "Expected delivery is tomorrow."
```

## Advanced Features

### Order Integration

Add and track customer orders:

```python
from whatsapp_context_manager import Order
from datetime import datetime, timedelta

# Add order to system
order = Order(
    order_id="ORD-12345",
    customer_id=context.customer.customer_id,
    status="shipped",
    amount=99.99,
    items=[
        {"name": "Wireless Headphones", "quantity": 1, "price": 99.99}
    ],
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat(),
    tracking_number="TRK-ABC123",
    estimated_delivery=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
)

manager.add_order(order)

# Now when customer asks about order, agent sees all details
context = manager.process_incoming_message(phone, "Order status?", agent_id)
print(context.active_orders[0].tracking_number)  # "TRK-ABC123"
```

### VIP Customer Management

Mark and manage VIP customers:

```python
# Update customer to VIP
manager.update_customer_info(
    phone="+1234567890",
    name="John Doe",
    email="john@example.com",
    is_vip=True,
    tags=["premium", "loyal", "high-value"],
    notes="Always responds best to quick, direct answers"
)

# Future messages automatically show VIP status
context = manager.process_incoming_message(phone, "Hello", agent_id)
print(context.customer.is_vip)  # True
print(context.customer.tags)    # ["premium", "loyal", "high-value"]
```

### Conversation History

Access complete conversation history:

```python
# Get context (includes recent messages)
context = manager.process_incoming_message(phone, "Need help", agent_id)

# View recent messages
for msg in context.recent_messages:
    direction = "Customer" if msg.direction == "inbound" else "Agent"
    print(f"{direction}: {msg.content}")
```

### Customer Profile

Access complete customer profile:

```python
context = manager.process_incoming_message(phone, "Hello", agent_id)

customer = context.customer
print(f"Phone: {customer.phone}")
print(f"Name: {customer.name}")
print(f"Total Messages: {customer.total_messages}")
print(f"VIP: {customer.is_vip}")
print(f"Tags: {customer.tags}")
print(f"Notes: {customer.notes}")
print(f"Last Contact: {customer.last_contact}")
print(f"Sentiment History: {customer.sentiment_history}")
```

## Common Use Cases

### Use Case 1: Order Status Inquiry

```python
# Customer: "Where is my order?"
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="Where is my order?",
    agent_id="agent_001"
)

# Agent sees:
if context.active_orders:
    order = context.active_orders[0]
    print(f"Order ID: {order.order_id}")
    print(f"Status: {order.status}")
    print(f"Tracking: {order.tracking_number}")
    print(f"Est. Delivery: {order.estimated_delivery}")

# Suggested response
print(context.suggested_responses[0])
# "Your order #ORD-12345 is shipped. Tracking: TRK-ABC123"
```

### Use Case 2: Angry Customer

```python
# Customer: "This is TERRIBLE! I want a refund NOW!!!"
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="This is TERRIBLE! I want a refund NOW!!!",
    agent_id="agent_001"
)

# System detects:
print(context.priority.value)   # "critical"
print(context.sentiment.value)  # "very_negative"

# Agent sees warnings:
for warning in context.warnings:
    print(warning)
# "🚨 CRITICAL: Requires immediate attention!"
# "😡 Customer is very upset - handle with care"

# Suggested response
print(context.suggested_responses[0])
# "I sincerely apologize for the inconvenience. Let me help resolve this."
```

### Use Case 3: Multiple Customers Priority Queue

```python
# Process messages from multiple customers
customers = [
    ("+1111111111", "Can I get some info?"),
    ("+2222222222", "My payment failed!!!"),
    ("+3333333333", "I have a complaint"),
    ("+4444444444", "Thanks for the help!"),
]

contexts = []
for phone, message in customers:
    context = manager.process_incoming_message(phone, message, "agent_001")
    contexts.append((phone, context))

# Sort by priority
priority_order = {
    MessagePriority.CRITICAL: 0,
    MessagePriority.HIGH: 1,
    MessagePriority.NORMAL: 2,
    MessagePriority.LOW: 3
}
contexts.sort(key=lambda x: priority_order[x[1].priority])

# Agent dashboard shows:
# 1. 🔴 +2222222222 - CRITICAL - Payment failed
# 2. 🟠 +3333333333 - HIGH - Complaint
# 3. 🟡 +1111111111 - NORMAL - Info request
# 4. 🟢 +4444444444 - LOW - Thank you message
```

### Use Case 4: First-time vs Returning Customer

```python
# System automatically tracks
context = manager.process_incoming_message(
    phone="+9999999999",  # New number
    message_content="Hello",
    agent_id="agent_001"
)

# Check if first time
if context.customer.total_messages == 1:
    print("👋 First time customer!")
    # Show introduction, onboarding info
else:
    print(f"📊 Returning customer ({context.customer.total_messages} messages)")
    # Show history, previous orders
```

## Integration Examples

### With WhatsApp Business API

```python
from whatsapp_business_api import WhatsAppClient
from whatsapp_context_manager import ContextManager

# Initialize
wa_client = WhatsAppClient(api_key="your_key")
manager = ContextManager("production.db")

# Handle incoming messages
@wa_client.on_message
def handle_message(phone, message):
    # Get context
    context = manager.process_incoming_message(
        phone=phone,
        message_content=message,
        agent_id="auto_agent"
    )
    
    # Display to agent dashboard
    display_to_agent(context)
    
    # If critical, alert supervisor
    if context.priority == MessagePriority.CRITICAL:
        notify_supervisor(context)
```

### With Web Dashboard

```python
from flask import Flask, jsonify
from whatsapp_context_manager import ContextManager

app = Flask(__name__)
manager = ContextManager()

@app.route('/api/message', methods=['POST'])
def process_message():
    data = request.json
    
    # Process message
    context = manager.process_incoming_message(
        phone=data['phone'],
        message_content=data['message'],
        agent_id=data['agent_id']
    )
    
    # Return context as JSON
    return jsonify(context.to_dict())
```

## Best Practices

### 1. Always Process Through System

```python
# Good ✅
context = manager.process_incoming_message(phone, message, agent_id)
# Agent has full context

# Bad ❌
# Responding without context
send_reply_directly(phone, "Hello")  # Agent is blind
```

### 2. Mark VIP Customers

```python
# Identify high-value customers early
if customer_is_high_value(phone):
    manager.update_customer_info(
        phone=phone,
        is_vip=True,
        tags=["high-value", "premium"]
    )
```

### 3. Track Orders

```python
# Add orders to system for automatic context
when_order_placed():
    manager.add_order(order)
    
# Now agents automatically see order status when customer asks
```

### 4. Use Suggested Responses

```python
# Get AI suggestions
context = manager.process_incoming_message(phone, message, agent_id)

# Show to agent for quick selection
for i, response in enumerate(context.suggested_responses, 1):
    print(f"{i}. {response}")
```

### 5. Monitor Priority Queue

```python
# Get all pending messages
pending_contexts = get_all_pending_messages()

# Sort by priority
pending_contexts.sort(key=lambda x: priority_order[x.priority])

# Agents work from top (critical) to bottom (low)
```

## Performance Tips

### 1. Database Management

```python
# Use separate databases for different purposes
dev_manager = ContextManager("development.db")
prod_manager = ContextManager("production.db")
test_manager = ContextManager("test.db")
```

### 2. Batch Processing

```python
# Process multiple messages efficiently
for phone, message in message_queue:
    context = manager.process_incoming_message(phone, message, agent_id)
    process_context(context)
```

### 3. Regular Cleanup

```python
# Archive old conversations (optional)
# System stores everything by default
# Implement custom archival if needed
```

## Security Features

- **Local Storage**: All data stored locally in SQLite
- **No External Dependencies**: Pure Python, no third-party libraries
- **Data Integrity**: SHA-256 checksums
- **Secure Queries**: Parameterized SQL, no injection risks
- **Privacy**: No data sent to external services

## Troubleshooting

### Issue: Database locked

```python
# Use different database per process
manager1 = ContextManager("agent1.db")
manager2 = ContextManager("agent2.db")
```

### Issue: Old data in tests

```python
# Clean up test databases
import os
if os.path.exists("test.db"):
    os.remove("test.db")
```

### Issue: No order suggestions

```python
# Make sure orders are added to system
order = Order(...)
manager.add_order(order)
```

## File Structure

```
whatsapp-context-manager/
├── whatsapp_context_manager.py  # Main library
├── examples_whatsapp.py         # 8 usage examples
├── test_whatsapp.py             # Complete test suite
├── README_WHATSAPP.md           # Full documentation
├── install_check_whatsapp.py    # Installation check
├── requirements_whatsapp.txt    # Dependencies (none!)
├── LICENSE_WHATSAPP             # MIT License
└── .gitignore_whatsapp          # Git ignore rules
```

## Requirements

- Python 3.8 or higher
- No external dependencies!

## Testing

```bash
# Run all tests
python test_whatsapp.py

# Should show:
# ✅ Sentiment analysis tests passed
# ✅ Message categorization tests passed
# ✅ Priority calculation tests passed
# ✅ Customer management tests passed
# ✅ Message storage tests passed
# ✅ Order management tests passed
# ✅ VIP customer tests passed
# ✅ Sentiment tracking tests passed
# ✅ Response suggestions tests passed
# ✅ Priority queue tests passed
# ✅ Conversation flow tests passed
# ✅ Context export tests passed
# ✅ ALL TESTS PASSED
```

## Examples

Run the examples to see the system in action:

```bash
python examples_whatsapp.py
```

Includes:
1. Basic message processing
2. Customer with active order
3. Angry customer scenario
4. VIP customer handling
5. Conversation history
6. Multiple customers priority queue
7. Agent dashboard view
8. Context export to JSON

## Getting Help

- 📖 Read full documentation: `README_WHATSAPP.md`
- 💻 Check examples: `examples_whatsapp.py`
- 🧪 Run tests: `test_whatsapp.py`
- 🐛 Report issues on GitHub
- ⭐ Star the repo if helpful!

## Next Steps

1. ✅ Install and verify: `python install_check_whatsapp.py`
2. ✅ Run tests: `python test_whatsapp.py`
3. ✅ Try examples: `python examples_whatsapp.py`
4. ✅ Integrate with your WhatsApp system
5. ✅ Customize for your needs

## License

MIT License - see `LICENSE_WHATSAPP` file

## Author

**cerbug45**
- GitHub: [@cerbug45](https://github.com/cerbug45)

---

**Transform your WhatsApp customer service from reactive to proactive!** 🚀
