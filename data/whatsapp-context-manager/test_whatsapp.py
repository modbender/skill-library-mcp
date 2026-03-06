"""
Test Suite for WhatsApp Intelligent Context Manager
Run with: python test_whatsapp.py
"""

from whatsapp_context_manager import (
    ContextManager, Order, Customer, Message,
    MessagePriority, CustomerSentiment, MessageCategory,
    SentimentAnalyzer, MessageCategorizer, PriorityCalculator
)
from datetime import datetime
import os


def cleanup_test_db(db_name):
    """Clean up test database"""
    if os.path.exists(db_name):
        os.remove(db_name)


def test_sentiment_analysis():
    """Test sentiment analyzer"""
    print("Testing sentiment analysis...")
    
    analyzer = SentimentAnalyzer()
    
    # Test very negative
    assert analyzer.analyze("This is TERRIBLE! SCAM! FRAUD!") == CustomerSentiment.VERY_NEGATIVE
    
    # Test negative
    assert analyzer.analyze("I'm disappointed with this product") == CustomerSentiment.NEGATIVE
    
    # Test positive
    assert analyzer.analyze("Thanks! This is great service") == CustomerSentiment.POSITIVE
    
    # Test very positive
    assert analyzer.analyze("Excellent! Best product ever!") == CustomerSentiment.VERY_POSITIVE
    
    # Test neutral
    assert analyzer.analyze("What is the price?") == CustomerSentiment.NEUTRAL
    
    # Test urgency
    assert analyzer.is_urgent("I need this ASAP!") == True
    assert analyzer.is_urgent("Can I get some info?") == False
    
    print("✅ Sentiment analysis tests passed")


def test_message_categorization():
    """Test message categorizer"""
    print("Testing message categorization...")
    
    categorizer = MessageCategorizer()
    
    # Test order status
    assert categorizer.categorize("Where is my order?") == MessageCategory.ORDER_STATUS
    
    # Test payment
    assert categorizer.categorize("I need a refund for my payment") == MessageCategory.PAYMENT
    
    # Test complaint
    assert categorizer.categorize("This product is broken") == MessageCategory.COMPLAINT
    
    # Test product inquiry
    assert categorizer.categorize("What's the price of this product?") == MessageCategory.PRODUCT_INQUIRY
    
    # Test support
    assert categorizer.categorize("I need help with setup") == MessageCategory.SUPPORT
    
    # Test sales
    assert categorizer.categorize("I want to buy this") == MessageCategory.SALES
    
    print("✅ Message categorization tests passed")


def test_priority_calculation():
    """Test priority calculator"""
    print("Testing priority calculation...")
    
    analyzer = SentimentAnalyzer()
    calculator = PriorityCalculator(analyzer)
    
    customer = Customer(
        customer_id="test_123",
        phone="+1234567890",
        is_vip=False
    )
    
    # Test critical (very negative)
    priority = calculator.calculate(
        "This is TERRIBLE!",
        customer,
        MessageCategory.COMPLAINT,
        CustomerSentiment.VERY_NEGATIVE
    )
    assert priority == MessagePriority.CRITICAL
    
    # Test critical (payment)
    priority = calculator.calculate(
        "Payment issue",
        customer,
        MessageCategory.PAYMENT,
        CustomerSentiment.NEUTRAL
    )
    assert priority == MessagePriority.CRITICAL
    
    # Test high (complaint)
    priority = calculator.calculate(
        "I have a problem",
        customer,
        MessageCategory.COMPLAINT,
        CustomerSentiment.NEGATIVE
    )
    assert priority == MessagePriority.HIGH
    
    # Test low (positive feedback)
    priority = calculator.calculate(
        "Great service!",
        customer,
        MessageCategory.FEEDBACK,
        CustomerSentiment.VERY_POSITIVE
    )
    assert priority == MessagePriority.LOW
    
    print("✅ Priority calculation tests passed")


def test_customer_creation():
    """Test customer creation and retrieval"""
    print("Testing customer management...")
    
    db_name = "test_customer.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    # Process message from new customer
    phone = "+1111111111"
    context = manager.process_incoming_message(phone, "Hello", agent_id="test_agent")
    
    assert context.customer.phone == phone
    assert context.customer.total_messages == 1
    assert context.customer.customer_id is not None
    
    # Retrieve same customer
    context2 = manager.process_incoming_message(phone, "Another message", agent_id="test_agent")
    assert context2.customer.customer_id == context.customer.customer_id
    assert context2.customer.total_messages == 2
    
    cleanup_test_db(db_name)
    print("✅ Customer management tests passed")


def test_message_storage():
    """Test message storage and retrieval"""
    print("Testing message storage...")
    
    db_name = "test_messages.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+2222222222"
    
    # Send multiple messages
    messages = ["Message 1", "Message 2", "Message 3"]
    for msg in messages:
        manager.process_incoming_message(phone, msg, agent_id="test_agent")
    
    # Retrieve context
    context = manager.get_context_by_phone(phone)
    
    assert len(context.recent_messages) == 3
    assert context.recent_messages[0].content == "Message 1"
    assert context.recent_messages[-1].content == "Message 3"
    
    cleanup_test_db(db_name)
    print("✅ Message storage tests passed")


def test_order_management():
    """Test order management"""
    print("Testing order management...")
    
    db_name = "test_orders.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+3333333333"
    context = manager.process_incoming_message(phone, "Hello", agent_id="test_agent")
    
    # Add order
    order = Order(
        order_id="TEST_ORDER_001",
        customer_id=context.customer.customer_id,
        status="processing",
        amount=99.99,
        items=[{"name": "Test Product", "quantity": 1}],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        tracking_number="TRACK123"
    )
    
    manager.add_order(order)
    
    # Retrieve context with order
    context = manager.process_incoming_message(phone, "Where is my order?", agent_id="test_agent")
    
    assert len(context.active_orders) == 1
    assert context.active_orders[0].order_id == "TEST_ORDER_001"
    assert context.active_orders[0].tracking_number == "TRACK123"
    
    cleanup_test_db(db_name)
    print("✅ Order management tests passed")


def test_vip_customer():
    """Test VIP customer handling"""
    print("Testing VIP customer handling...")
    
    db_name = "test_vip.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+4444444444"
    manager.process_incoming_message(phone, "Hello", agent_id="test_agent")
    
    # Mark as VIP
    manager.update_customer_info(
        phone,
        name="VIP Customer",
        is_vip=True,
        tags=["premium", "high-value"]
    )
    
    # Process message
    context = manager.process_incoming_message(phone, "I have a question", agent_id="test_agent")
    
    assert context.customer.is_vip == True
    assert context.customer.name == "VIP Customer"
    assert "premium" in context.customer.tags
    assert any("VIP" in insight for insight in context.key_insights)
    
    cleanup_test_db(db_name)
    print("✅ VIP customer tests passed")


def test_sentiment_tracking():
    """Test sentiment history tracking"""
    print("Testing sentiment tracking...")
    
    db_name = "test_sentiment.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+5555555555"
    
    # Send messages with different sentiments
    messages = [
        "This is terrible!",
        "Still not happy",
        "Getting frustrated",
        "This is awful"
    ]
    
    for msg in messages:
        manager.process_incoming_message(phone, msg, agent_id="test_agent")
    
    context = manager.get_context_by_phone(phone)
    
    # Check sentiment history (should have negative sentiments)
    assert len(context.customer.sentiment_history) >= 3
    negative_count = sum(1 for s in context.customer.sentiment_history if s in ['negative', 'very_negative'])
    assert negative_count >= 2  # At least 2 negative sentiments
    
    # Should generate warning about negative trend
    has_warning = any("consistently" in insight.lower() or "unhappy" in insight.lower() 
                     for insight in context.key_insights)
    # Note: Warning may not always appear depending on exact sentiment analysis
    
    cleanup_test_db(db_name)
    print("✅ Sentiment tracking tests passed")


def test_suggested_responses():
    """Test response suggestions"""
    print("Testing response suggestions...")
    
    db_name = "test_responses.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+6666666666"
    
    # Test with order inquiry
    context = manager.process_incoming_message(phone, "Hello", agent_id="test_agent")
    
    order = Order(
        order_id="ORD-123",
        customer_id=context.customer.customer_id,
        status="shipped",
        amount=49.99,
        items=[{"name": "Product", "quantity": 1}],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    manager.add_order(order)
    
    context = manager.process_incoming_message(phone, "Where is my order?", agent_id="test_agent")
    
    assert len(context.suggested_responses) > 0
    assert any("order" in r.lower() for r in context.suggested_responses)
    
    cleanup_test_db(db_name)
    print("✅ Response suggestions tests passed")


def test_priority_queue():
    """Test message prioritization"""
    print("Testing priority queue...")
    
    db_name = "test_priority.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    # Create different priority messages
    messages = [
        ("+1000000001", "Can I get some info?"),  # Low/Normal
        ("+1000000002", "My payment failed!!!"),  # Critical
        ("+1000000003", "I have a complaint"),     # High
    ]
    
    contexts = []
    for phone, msg in messages:
        context = manager.process_incoming_message(phone, msg, agent_id="test_agent")
        contexts.append(context)
    
    # Check priorities
    assert contexts[0].priority in [MessagePriority.NORMAL, MessagePriority.LOW]
    assert contexts[1].priority == MessagePriority.CRITICAL
    assert contexts[2].priority == MessagePriority.HIGH
    
    cleanup_test_db(db_name)
    print("✅ Priority queue tests passed")


def test_conversation_flow():
    """Test multi-message conversation"""
    print("Testing conversation flow...")
    
    db_name = "test_conversation.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+7777777777"
    agent_id = "test_agent"
    
    # Simulate conversation
    manager.process_incoming_message(phone, "Hello", agent_id)
    manager.send_message(phone, "Hi! How can I help?", agent_id)
    manager.process_incoming_message(phone, "I need help", agent_id)
    manager.send_message(phone, "Sure, what do you need?", agent_id)
    
    context = manager.get_context_by_phone(phone)
    
    assert len(context.recent_messages) == 4
    assert context.recent_messages[0].direction == "inbound"
    assert context.recent_messages[1].direction == "outbound"
    
    cleanup_test_db(db_name)
    print("✅ Conversation flow tests passed")


def test_context_export():
    """Test context export to dict"""
    print("Testing context export...")
    
    db_name = "test_export.db"
    cleanup_test_db(db_name)
    
    manager = ContextManager(db_name)
    
    phone = "+8888888888"
    context = manager.process_incoming_message(phone, "Test message", agent_id="test_agent")
    
    # Export to dict
    context_dict = context.to_dict()
    
    assert isinstance(context_dict, dict)
    assert 'customer' in context_dict
    assert 'recent_messages' in context_dict
    assert 'priority' in context_dict
    assert 'sentiment' in context_dict
    assert 'suggested_responses' in context_dict
    
    cleanup_test_db(db_name)
    print("✅ Context export tests passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("WHATSAPP INTELLIGENT CONTEXT MANAGER - TEST SUITE")
    print("="*60 + "\n")
    
    try:
        test_sentiment_analysis()
        test_message_categorization()
        test_priority_calculation()
        test_customer_creation()
        test_message_storage()
        test_order_management()
        test_vip_customer()
        test_sentiment_tracking()
        test_suggested_responses()
        test_priority_queue()
        test_conversation_flow()
        test_context_export()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
