# WhatsApp Intelligent Context Manager

A secure, AI-powered context management system for WhatsApp customer service agents. Get instant, comprehensive customer insights to deliver better, faster support.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What Problem Does This Solve?

**The Agent's Nightmare:**
- ❌ Customer says "I told you last week..." — Agent has no idea what they're talking about
- ❌ Switching between WhatsApp, CRM, order system, notes
- ❌ Not knowing if customer is VIP or first-timer
- ❌ Missing urgent messages buried in hundreds of chats
- ❌ Guessing what to say instead of having smart suggestions

**With This System:**
- ✅ **Instant Context**: See complete customer history in 2 seconds
- ✅ **Smart Prioritization**: Angry customers flagged immediately
- ✅ **AI Analysis**: Sentiment, category, urgency automatically detected
- ✅ **Response Suggestions**: Get smart reply recommendations
- ✅ **Order Integration**: See order status without leaving chat
- ✅ **VIP Detection**: Know who your important customers are

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cerbug45/whatsapp-context-manager.git
cd whatsapp-context-manager

# No dependencies needed - pure Python standard library!
python test_whatsapp.py  # Verify installation
```

### Basic Usage

```python
from whatsapp_context_manager import ContextManager

# Initialize
manager = ContextManager()

# When a WhatsApp message arrives
context = manager.process_incoming_message(
    phone="+1234567890",
    message_content="Where is my order?!",
    agent_id="agent_001"
)

# Get instant insights
print(f"Priority: {context.priority.value}")  # "critical"
print(f"Sentiment: {context.sentiment.value}")  # "negative"
print(f"VIP Customer: {context.customer.is_vip}")  # True/False

# See what agent needs to know
for insight in context.key_insights:
    print(f"💡 {insight}")

# Get suggested responses
for response in context.suggested_responses:
    print(f"💬 {response}")
```

## 📊 What You Get - Agent Dashboard

When a message arrives, agents instantly see:

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

## 🔥 Key Features

### 1. **Intelligent Sentiment Analysis**
Automatically detects customer mood:
- 😡 Very Negative (angry, furious, scam)
- 😟 Negative (disappointed, problem)
- 😐 Neutral (questions, info requests)
- 😊 Positive (thanks, happy)
- 🤩 Very Positive (excellent, love it)

### 2. **Automatic Message Categorization**
- 📦 Order Status
- 💳 Payment Issues
- 🔴 Complaints
- 🛍️ Product Inquiries
- 🆘 Support Requests
- 💰 Sales
- ⭐ Feedback

### 3. **Smart Priority System**
- 🔴 **CRITICAL**: Angry customer, payment issue, VIP unhappy
- 🟠 **HIGH**: Complaints, negative sentiment
- 🟡 **NORMAL**: General questions
- 🟢 **LOW**: Info requests, positive feedback

### 4. **Context Intelligence**
- Complete conversation history
- Active order tracking
- Last issue resolution
- Sentiment trend analysis
- Response time expectations

### 5. **AI-Powered Response Suggestions**
Based on:
- Message category
- Customer history
- Current orders
- Past successful responses

### 6. **Security Features**
- SHA-256 data integrity
- SQLite with secure queries
- No external dependencies
- Local data storage
- GDPR-ready architecture

## 📚 Core Components

### ContextManager
Main interface for agents

```python
manager = ContextManager("production.db")

# Process incoming message
context = manager.process_incoming_message(phone, message, agent_id)

# Send reply
manager.send_message(phone, "Thanks for your patience!", agent_id)

# Add order
manager.add_order(order)

# Update customer info
manager.update_customer_info(phone, name="John", is_vip=True)
```

### Customer Profile
```python
customer = context.customer
customer.phone           # Phone number
customer.name            # Customer name
customer.is_vip          # VIP status
customer.tags            # ["premium", "loyal"]
customer.notes           # Special notes
customer.total_messages  # Message count
customer.sentiment_history  # Recent sentiments
```

### Context Summary
```python
context.priority         # Message priority
context.sentiment        # Customer sentiment
context.customer         # Customer profile
context.recent_messages  # Last 10 messages
context.active_orders    # Current orders
context.key_insights     # What agent needs to know
context.warnings         # Urgent alerts
context.suggested_responses  # Smart replies
```

## 🎯 Use Cases

### Use Case 1: Order Status Inquiry
```python
# Customer: "Where is my order?"
context = manager.process_incoming_message(phone, message, agent_id)

# Agent sees:
# - Order #12345 is "shipped"
# - Tracking: TRK-123
# - Estimated delivery: Tomorrow
# - Suggested: "Your order is on the way! Tracking: TRK-123"
```

### Use Case 2: Angry Customer
```python
# Customer: "This is TERRIBLE! I want a refund NOW!!!"
context = manager.process_incoming_message(phone, message, agent_id)

# System detects:
# - Priority: CRITICAL
# - Sentiment: VERY_NEGATIVE
# - Warning: Customer is very upset
# - Suggested: "I sincerely apologize for the inconvenience..."
```

### Use Case 3: VIP Customer
```python
# VIP customer messages
context = manager.process_incoming_message(phone, message, agent_id)

# Agent sees:
# - 🌟 VIP Customer badge
# - Complete purchase history
# - Previous preferences
# - Personalized response suggestions
```

### Use Case 4: Multiple Customers
```python
# Agent dashboard shows priority queue:
# 1. 🔴 +123-XXX-1111 - CRITICAL - Angry about payment
# 2. 🟠 +123-XXX-2222 - HIGH - Complaint
# 3. 🟡 +123-XXX-3333 - NORMAL - Product question
# 4. 🟢 +123-XXX-4444 - LOW - Thank you message
```

## 🔧 Advanced Features

### Order Integration
```python
order = Order(
    order_id="ORD-12345",
    customer_id=customer.customer_id,
    status="shipped",
    amount=99.99,
    items=[{"name": "Product", "quantity": 1}],
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat(),
    tracking_number="TRK-123",
    estimated_delivery="2024-12-25"
)

manager.add_order(order)
```

### Customer Tagging
```python
manager.update_customer_info(
    phone="+1234567890",
    name="John Doe",
    email="john@example.com",
    is_vip=True,
    tags=["premium", "loyal", "high-value"],
    notes="Always responds best to quick, direct answers"
)
```

### Export Context
```python
# Export for API integration
context_dict = context.to_dict()
json_data = json.dumps(context_dict, indent=2)
```

## 📊 Analytics & Insights

The system automatically tracks:
- Total customer messages
- Average response time expectations
- Sentiment trends
- Category patterns
- VIP customer interactions
- Priority distribution

## 🛡️ Security

- **Data Integrity**: SHA-256 checksums
- **Local Storage**: All data stored locally in SQLite
- **No External Dependencies**: Pure Python, no third-party libs
- **Secure Queries**: Parameterized SQL, no injection risks
- **Privacy First**: No data sent to external services

## 🧪 Testing

```bash
# Run complete test suite
python test_whatsapp.py

# Run examples
python examples_whatsapp.py
```

All tests included:
- ✅ Sentiment analysis
- ✅ Message categorization
- ✅ Priority calculation
- ✅ Customer management
- ✅ Order tracking
- ✅ VIP handling
- ✅ Conversation flow

## 📖 Examples

Check `examples_whatsapp.py` for:
1. Basic message processing
2. Customer with orders
3. Angry customer handling
4. VIP customer management
5. Conversation history
6. Multiple customers priority queue
7. Agent dashboard view
8. JSON export

## 🎨 Integration

### With WhatsApp Business API
```python
from whatsapp_business_api import WhatsAppClient
from whatsapp_context_manager import ContextManager

wa_client = WhatsAppClient(api_key="your_key")
manager = ContextManager()

@wa_client.on_message
def handle_message(phone, message):
    # Get context
    context = manager.process_incoming_message(phone, message, "agent_001")
    
    # Show to agent (your UI)
    display_context_to_agent(context)
    
    # Agent replies
    agent_response = get_agent_response()
    
    # Send and log
    wa_client.send_message(phone, agent_response)
    manager.send_message(phone, agent_response, "agent_001")
```

### With CRM Systems
```python
# Sync with your CRM
context = manager.process_incoming_message(phone, message, agent_id)

# Update CRM
crm.update_customer(
    phone=context.customer.phone,
    last_contact=context.customer.last_contact,
    sentiment=context.sentiment.value,
    notes=context.warnings
)
```

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 👨‍💻 Author

**cerbug45**
- GitHub: [@cerbug45](https://github.com/cerbug45)

## 🙏 Acknowledgments

Built for customer service teams who want to:
- Reduce response times
- Improve customer satisfaction
- Handle more customers with same team
- Never miss important context again

## 📞 Support

- 📖 Read the full documentation
- 🐛 Report issues on GitHub
- 💡 Request features via GitHub Issues
- ⭐ Star the repo if you find it useful!

---

**Transform your WhatsApp customer service from chaotic to systematic.** 🚀
