"""
Examples for WhatsApp Intelligent Context Manager
Demonstrates various use cases and features
"""

from whatsapp_context_manager import (
    ContextManager, Order, MessagePriority, CustomerSentiment
)
from datetime import datetime, timedelta
import json


def example_1_basic_usage():
    """Example 1: Basic message processing"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Message Processing")
    print("="*60 + "\n")
    
    # Initialize context manager
    manager = ContextManager("example1.db")
    
    # Simulate incoming message from customer
    phone = "+1234567890"
    message = "Hi, where is my order? I've been waiting for days!"
    
    print(f"📱 Incoming message from {phone}:")
    print(f"   '{message}'\n")
    
    # Process message and get context
    context = manager.process_incoming_message(phone, message, agent_id="agent_001")
    
    print("🔍 CONTEXT ANALYSIS:")
    print(f"   Priority: {context.priority.value.upper()}")
    print(f"   Sentiment: {context.sentiment.value}")
    print(f"   Customer: {context.customer.phone}")
    print(f"   Total Messages: {context.customer.total_messages}")
    
    print("\n💡 KEY INSIGHTS:")
    for insight in context.key_insights:
        print(f"   {insight}")
    
    print("\n⚠️ WARNINGS:")
    for warning in context.warnings:
        print(f"   {warning}")
    
    print("\n💬 SUGGESTED RESPONSES:")
    for i, response in enumerate(context.suggested_responses, 1):
        print(f"   {i}. {response}")


def example_2_with_order():
    """Example 2: Customer with active order"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Customer with Active Order")
    print("="*60 + "\n")
    
    manager = ContextManager("example2.db")
    
    # Create a customer with an order
    phone = "+1987654321"
    message = "When will my package arrive?"
    
    # First, add an order for this customer
    context = manager.process_incoming_message(phone, "Hello", agent_id="agent_002")
    
    order = Order(
        order_id="ORD-12345",
        customer_id=context.customer.customer_id,
        status="shipped",
        amount=99.99,
        items=[{"name": "Wireless Headphones", "quantity": 1}],
        created_at=(datetime.now() - timedelta(days=3)).isoformat(),
        updated_at=datetime.now().isoformat(),
        tracking_number="TRK-ABC123",
        estimated_delivery=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    )
    
    manager.add_order(order)
    
    # Now process the order inquiry
    context = manager.process_incoming_message(phone, message, agent_id="agent_002")
    
    print(f"📱 Customer: {phone}")
    print(f"📦 Active Orders: {len(context.active_orders)}\n")
    
    if context.active_orders:
        order = context.active_orders[0]
        print(f"ORDER DETAILS:")
        print(f"   Order ID: {order.order_id}")
        print(f"   Status: {order.status}")
        print(f"   Amount: ${order.amount}")
        print(f"   Tracking: {order.tracking_number}")
        print(f"   Est. Delivery: {order.estimated_delivery}")
    
    print(f"\n💡 KEY INSIGHTS:")
    for insight in context.key_insights:
        print(f"   {insight}")
    
    print(f"\n💬 SUGGESTED RESPONSES:")
    for i, response in enumerate(context.suggested_responses, 1):
        print(f"   {i}. {response}")


def example_3_angry_customer():
    """Example 3: Handling angry customer"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Angry Customer Scenario")
    print("="*60 + "\n")
    
    manager = ContextManager("example3.db")
    
    phone = "+1555123456"
    
    # Simulate escalating conversation
    messages = [
        "I have a problem with my order",
        "This is taking too long! I've been waiting for a response",
        "This is TERRIBLE service! I want a refund NOW!!! SCAM!!!"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n📱 Message {i}: '{msg}'")
        context = manager.process_incoming_message(phone, msg, agent_id="agent_003")
        
        print(f"   Priority: {context.priority.value.upper()}")
        print(f"   Sentiment: {context.sentiment.value}")
        
        if context.warnings:
            print(f"   ⚠️ Warnings:")
            for warning in context.warnings:
                print(f"      {warning}")


def example_4_vip_customer():
    """Example 4: VIP customer handling"""
    print("\n" + "="*60)
    print("EXAMPLE 4: VIP Customer")
    print("="*60 + "\n")
    
    manager = ContextManager("example4.db")
    
    phone = "+1999888777"
    
    # First contact
    context = manager.process_incoming_message(
        phone, 
        "Hello, I'd like to know about your premium products",
        agent_id="agent_004"
    )
    
    # Mark as VIP
    manager.update_customer_info(
        phone,
        name="John Doe",
        email="john@example.com",
        is_vip=True,
        tags=["premium", "high-value"],
        notes="Important client - always prioritize"
    )
    
    # Next message
    context = manager.process_incoming_message(
        phone,
        "I have a question about my order",
        agent_id="agent_004"
    )
    
    print(f"📱 Customer: {context.customer.name}")
    print(f"   Phone: {context.customer.phone}")
    print(f"   Email: {context.customer.email}")
    print(f"   VIP Status: {'YES' if context.customer.is_vip else 'NO'}")
    print(f"   Tags: {', '.join(context.customer.tags)}")
    
    print(f"\n💡 KEY INSIGHTS:")
    for insight in context.key_insights:
        print(f"   {insight}")
    
    print(f"\n💬 SUGGESTED RESPONSES:")
    for i, response in enumerate(context.suggested_responses, 1):
        print(f"   {i}. {response}")


def example_5_conversation_history():
    """Example 5: Multi-message conversation"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Conversation History")
    print("="*60 + "\n")
    
    manager = ContextManager("example5.db")
    
    phone = "+1777666555"
    agent_id = "agent_005"
    
    # Simulate conversation
    conversation = [
        ("inbound", "Hi, I want to buy a laptop"),
        ("outbound", "Great! What specifications are you looking for?"),
        ("inbound", "I need 16GB RAM and good battery life"),
        ("outbound", "I have several options. What's your budget?"),
        ("inbound", "Around $1000"),
        ("outbound", "Perfect! I'll send you our recommendations."),
        ("inbound", "Thanks! Also, do you offer warranty?"),
    ]
    
    print("📱 CONVERSATION:\n")
    
    for direction, message in conversation:
        if direction == "inbound":
            print(f"👤 Customer: {message}")
            context = manager.process_incoming_message(phone, message, agent_id)
        else:
            print(f"👨‍💼 Agent: {message}")
            manager.send_message(phone, message, agent_id)
    
    print(f"\n📊 CONVERSATION SUMMARY:")
    print(f"   Total Messages: {context.customer.total_messages}")
    print(f"   Messages in History: {len(context.recent_messages)}")
    
    print(f"\n📜 RECENT MESSAGE HISTORY:")
    for msg in context.recent_messages[-5:]:  # Last 5 messages
        direction_icon = "👤" if msg.direction == "inbound" else "👨‍💼"
        print(f"   {direction_icon} [{msg.timestamp[:19]}] {msg.content[:50]}...")


def example_6_multiple_customers():
    """Example 6: Managing multiple customers"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Multiple Customers - Priority Queue")
    print("="*60 + "\n")
    
    manager = ContextManager("example6.db")
    
    # Simulate messages from different customers
    customers = [
        ("+1111111111", "Hi, I have a question", "normal"),
        ("+2222222222", "My payment didn't go through!!!", "critical"),
        ("+3333333333", "Thanks for the great service!", "positive"),
        ("+4444444444", "WHERE IS MY ORDER?! This is UNACCEPTABLE!", "angry"),
        ("+5555555555", "Can you tell me the price?", "inquiry"),
    ]
    
    contexts = []
    for phone, message, label in customers:
        context = manager.process_incoming_message(phone, message, agent_id="agent_006")
        contexts.append((phone, context, label))
    
    # Sort by priority
    priority_order = {
        MessagePriority.CRITICAL: 0,
        MessagePriority.HIGH: 1,
        MessagePriority.NORMAL: 2,
        MessagePriority.LOW: 3
    }
    
    contexts.sort(key=lambda x: priority_order[x[1].priority])
    
    print("📋 PRIORITY QUEUE (Highest to Lowest):\n")
    
    for i, (phone, context, label) in enumerate(contexts, 1):
        priority_emoji = {
            MessagePriority.CRITICAL: "🔴",
            MessagePriority.HIGH: "🟠",
            MessagePriority.NORMAL: "🟡",
            MessagePriority.LOW: "🟢"
        }
        
        print(f"{i}. {priority_emoji[context.priority]} {phone}")
        print(f"   Priority: {context.priority.value.upper()}")
        print(f"   Sentiment: {context.sentiment.value}")
        print(f"   Category: {context.recent_messages[-1].category.value if context.recent_messages else 'N/A'}")
        if context.warnings:
            print(f"   ⚠️ {context.warnings[0]}")
        print()


def example_7_agent_dashboard():
    """Example 7: Agent dashboard view"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Agent Dashboard")
    print("="*60 + "\n")
    
    manager = ContextManager("example7.db")
    
    phone = "+1234567890"
    
    # Simulate some history
    manager.process_incoming_message(phone, "Hello", agent_id="agent_007")
    
    order = Order(
        order_id="ORD-99999",
        customer_id=manager.db.get_customer_by_phone(phone).customer_id,
        status="processing",
        amount=149.99,
        items=[{"name": "Smart Watch", "quantity": 1}],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    manager.add_order(order)
    
    context = manager.process_incoming_message(
        phone, 
        "I need help with my order urgently!",
        agent_id="agent_007"
    )
    
    # Display dashboard
    print("┌" + "─"*58 + "┐")
    print("│" + " "*15 + "AGENT DASHBOARD" + " "*28 + "│")
    print("├" + "─"*58 + "┤")
    print(f"│ Customer: {context.customer.phone:<44}│")
    print(f"│ Name: {context.customer.name or 'N/A':<48}│")
    print(f"│ VIP: {'YES' if context.customer.is_vip else 'NO':<49}│")
    print("├" + "─"*58 + "┤")
    print(f"│ Priority: {context.priority.value.upper():<46}│")
    print(f"│ Sentiment: {context.sentiment.value:<45}│")
    print("├" + "─"*58 + "┤")
    print("│ KEY INSIGHTS:" + " "*44 + "│")
    for insight in context.key_insights[:3]:
        print(f"│   • {insight:<53}│")
    print("├" + "─"*58 + "┤")
    print("│ WARNINGS:" + " "*48 + "│")
    for warning in context.warnings[:2]:
        print(f"│   • {warning:<53}│")
    print("├" + "─"*58 + "┤")
    print("│ SUGGESTED RESPONSES:" + " "*37 + "│")
    for i, response in enumerate(context.suggested_responses[:2], 1):
        print(f"│   {i}. {response:<53}│")
    print("└" + "─"*58 + "┘")


def example_8_export_context():
    """Example 8: Export context as JSON"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Export Context to JSON")
    print("="*60 + "\n")
    
    manager = ContextManager("example8.db")
    
    phone = "+1999999999"
    context = manager.process_incoming_message(
        phone,
        "I need help with payment issues",
        agent_id="agent_008"
    )
    
    # Export to JSON
    context_json = json.dumps(context.to_dict(), indent=2)
    
    print("📄 Context exported to JSON format:\n")
    print(context_json[:500] + "...")  # Show first 500 chars
    
    print(f"\n✅ Full context can be exported for:")
    print(f"   • Integration with other systems")
    print(f"   • API responses")
    print(f"   • Logging and analytics")
    print(f"   • Machine learning training data")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("WHATSAPP INTELLIGENT CONTEXT MANAGER - EXAMPLES")
    print("="*60)
    
    example_1_basic_usage()
    example_2_with_order()
    example_3_angry_customer()
    example_4_vip_customer()
    example_5_conversation_history()
    example_6_multiple_customers()
    example_7_agent_dashboard()
    example_8_export_context()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60 + "\n")
    
    print("💡 TIP: Check the *.db files created to see the stored data")
    print("🧹 Clean up: Delete example*.db files when done")


if __name__ == "__main__":
    main()
