"""
WhatsApp Intelligent Context Manager
A secure, AI-powered context management system for WhatsApp customer service agents

Author: cerbug45
License: MIT
"""

import json
import hashlib
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import re
from collections import defaultdict
import os


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = "critical"  # Angry customer, payment issue
    HIGH = "high"          # Complaint, urgent request
    NORMAL = "normal"      # General questions
    LOW = "low"            # Info request, FAQ


class CustomerSentiment(Enum):
    """Customer sentiment analysis"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class MessageCategory(Enum):
    """Message categories"""
    ORDER_STATUS = "order_status"
    COMPLAINT = "complaint"
    PAYMENT = "payment"
    PRODUCT_INQUIRY = "product_inquiry"
    SUPPORT = "support"
    SALES = "sales"
    FEEDBACK = "feedback"
    OTHER = "other"


@dataclass
class Customer:
    """Customer profile"""
    customer_id: str
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    is_vip: bool = False
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_contact: Optional[str] = None
    total_messages: int = 0
    avg_response_time: float = 0.0  # in seconds
    sentiment_history: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Message:
    """Single WhatsApp message"""
    message_id: str
    customer_id: str
    content: str
    direction: str  # "inbound" or "outbound"
    timestamp: str
    agent_id: Optional[str] = None
    category: Optional[MessageCategory] = None
    sentiment: Optional[CustomerSentiment] = None
    priority: Optional[MessagePriority] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.category:
            data['category'] = self.category.value
        if self.sentiment:
            data['sentiment'] = self.sentiment.value
        if self.priority:
            data['priority'] = self.priority.value
        return data


@dataclass
class Order:
    """Customer order information"""
    order_id: str
    customer_id: str
    status: str
    amount: float
    items: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContextSummary:
    """Complete context summary for agent"""
    customer: Customer
    recent_messages: List[Message]
    active_orders: List[Order]
    last_issue: Optional[Dict[str, Any]]
    suggested_responses: List[str]
    priority: MessagePriority
    sentiment: CustomerSentiment
    key_insights: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'customer': self.customer.to_dict(),
            'recent_messages': [m.to_dict() for m in self.recent_messages],
            'active_orders': [o.to_dict() for o in self.active_orders],
            'last_issue': self.last_issue,
            'suggested_responses': self.suggested_responses,
            'priority': self.priority.value,
            'sentiment': self.sentiment.value,
            'key_insights': self.key_insights,
            'warnings': self.warnings
        }


class SentimentAnalyzer:
    """Analyze customer sentiment from WhatsApp messages"""
    
    def __init__(self):
        # Negative indicators
        self.very_negative_words = [
            'angry', 'furious', 'terrible', 'worst', 'horrible', 'disgusting',
            'pathetic', 'useless', 'scam', 'fraud', 'lawsuit', 'lawyer',
            'never again', 'cancel', 'refund now'
        ]
        self.negative_words = [
            'disappointed', 'unhappy', 'problem', 'issue', 'complaint',
            'wrong', 'mistake', 'error', 'broken', 'not working', 'bad',
            'poor', 'unsatisfied', 'upset', 'frustrated'
        ]
        
        # Positive indicators
        self.very_positive_words = [
            'excellent', 'amazing', 'perfect', 'outstanding', 'fantastic',
            'love', 'best', 'wonderful', 'brilliant', 'superb', 'awesome'
        ]
        self.positive_words = [
            'good', 'great', 'nice', 'thanks', 'thank you', 'appreciate',
            'happy', 'satisfied', 'pleased', 'helpful', 'fast', 'quick'
        ]
        
        # Urgent indicators
        self.urgent_indicators = [
            'urgent', 'asap', 'immediately', 'now', 'emergency',
            'quickly', 'hurry', 'waiting', 'still waiting', 'been waiting'
        ]
    
    def analyze(self, message: str) -> CustomerSentiment:
        """Analyze sentiment of a message"""
        message_lower = message.lower()
        
        # Check for very negative
        for word in self.very_negative_words:
            if word in message_lower:
                return CustomerSentiment.VERY_NEGATIVE
        
        # Check for very positive
        for word in self.very_positive_words:
            if word in message_lower:
                return CustomerSentiment.VERY_POSITIVE
        
        # Count negative and positive
        negative_count = sum(1 for word in self.negative_words if word in message_lower)
        positive_count = sum(1 for word in self.positive_words if word in message_lower)
        
        # Check for exclamation marks and caps (indicates emotion)
        exclamation_count = message.count('!')
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        
        if negative_count > 0 and (exclamation_count > 2 or caps_ratio > 0.5):
            return CustomerSentiment.VERY_NEGATIVE
        
        if negative_count > positive_count:
            return CustomerSentiment.NEGATIVE
        elif positive_count > negative_count:
            return CustomerSentiment.POSITIVE
        else:
            return CustomerSentiment.NEUTRAL
    
    def is_urgent(self, message: str) -> bool:
        """Check if message is urgent"""
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in self.urgent_indicators)


class MessageCategorizer:
    """Categorize WhatsApp messages automatically"""
    
    def __init__(self):
        self.category_keywords = {
            MessageCategory.ORDER_STATUS: [
                'order', 'delivery', 'shipped', 'tracking', 'when will',
                'where is', 'arrived', 'package', 'cargo', 'shipment',
                'track', 'status', 'receive'
            ],
            MessageCategory.PAYMENT: [
                'payment', 'paid', 'refund', 'money', 'charge', 'credit card',
                'invoice', 'receipt', 'billing', 'transaction', 'bank',
                'paypal', 'pay'
            ],
            MessageCategory.COMPLAINT: [
                'complaint', 'problem', 'issue', 'wrong', 'broken',
                'not working', 'disappointed', 'unhappy', 'defective',
                'damaged', 'missing'
            ],
            MessageCategory.PRODUCT_INQUIRY: [
                'product', 'price', 'available', 'stock', 'specifications',
                'features', 'details', 'info', 'information', 'size',
                'color', 'model'
            ],
            MessageCategory.SUPPORT: [
                'help', 'support', 'how to', 'question', 'confused',
                'explain', 'understand', 'guide', 'tutorial'
            ],
            MessageCategory.SALES: [
                'buy', 'purchase', 'order', 'want', 'interested',
                'price', 'cost', 'checkout', 'cart'
            ],
            MessageCategory.FEEDBACK: [
                'feedback', 'review', 'rating', 'opinion', 'suggest',
                'recommend', 'experience'
            ]
        }
    
    def categorize(self, message: str) -> MessageCategory:
        """Categorize a message"""
        message_lower = message.lower()
        
        scores = defaultdict(int)
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[category] += 1
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return MessageCategory.OTHER


class PriorityCalculator:
    """Calculate message priority"""
    
    def __init__(self, sentiment_analyzer: SentimentAnalyzer):
        self.sentiment_analyzer = sentiment_analyzer
    
    def calculate(
        self,
        message: str,
        customer: Customer,
        category: MessageCategory,
        sentiment: CustomerSentiment
    ) -> MessagePriority:
        """Calculate priority based on multiple factors"""
        
        # Critical if very negative sentiment
        if sentiment == CustomerSentiment.VERY_NEGATIVE:
            return MessagePriority.CRITICAL
        
        # Critical if VIP customer with negative sentiment
        if customer.is_vip and sentiment == CustomerSentiment.NEGATIVE:
            return MessagePriority.CRITICAL
        
        # Critical if payment issue
        if category == MessageCategory.PAYMENT:
            return MessagePriority.CRITICAL
        
        # Critical if urgent indicator
        if self.sentiment_analyzer.is_urgent(message):
            return MessagePriority.CRITICAL
        
        # High if complaint
        if category == MessageCategory.COMPLAINT:
            return MessagePriority.HIGH
        
        # High if negative sentiment
        if sentiment == CustomerSentiment.NEGATIVE:
            return MessagePriority.HIGH
        
        # Low if feedback or very positive
        if category == MessageCategory.FEEDBACK or sentiment == CustomerSentiment.VERY_POSITIVE:
            return MessagePriority.LOW
        
        # Default to normal
        return MessagePriority.NORMAL


class ResponseSuggester:
    """Suggest responses based on context"""
    
    def __init__(self):
        self.templates = {
            MessageCategory.ORDER_STATUS: [
                "Let me check your order status right away.",
                "I can see your order #{order_id}. It's currently {status}.",
                "Your order is on the way! Tracking number: {tracking}",
                "Expected delivery is {delivery_date}."
            ],
            MessageCategory.PAYMENT: [
                "I'll look into the payment issue immediately.",
                "Let me verify your payment of ${amount}.",
                "Your refund has been processed and should arrive in 3-5 business days.",
                "I can confirm your payment was received successfully."
            ],
            MessageCategory.COMPLAINT: [
                "I sincerely apologize for the inconvenience.",
                "I understand your frustration, let me help resolve this.",
                "This is not the experience we want for our customers. Let me fix this.",
                "I'll escalate this to our management team right away."
            ],
            MessageCategory.PRODUCT_INQUIRY: [
                "That product is currently in stock!",
                "The price for that item is ${price}.",
                "Let me share the specifications with you.",
                "Would you like me to send you more information about this product?"
            ],
            MessageCategory.SUPPORT: [
                "I'd be happy to help you with that.",
                "Let me guide you through this step by step.",
                "Here's how you can do that:",
                "Is there anything specific you'd like to know?"
            ]
        }
    
    def suggest(
        self,
        category: MessageCategory,
        customer: Customer,
        recent_messages: List[Message],
        orders: List[Order]
    ) -> List[str]:
        """Suggest appropriate responses"""
        suggestions = []
        
        # Get base templates for category
        if category in self.templates:
            suggestions.extend(self.templates[category][:2])
        
        # Add order-specific suggestions
        if orders:
            latest_order = orders[0]
            suggestions.append(
                f"Your order #{latest_order.order_id} is {latest_order.status}."
            )
            if latest_order.tracking_number:
                suggestions.append(
                    f"Tracking: {latest_order.tracking_number}"
                )
        
        # Add VIP greeting if applicable
        if customer.is_vip and not suggestions:
            suggestions.append(
                f"Hello {customer.name or 'valued customer'}, how can I assist you today?"
            )
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "How can I help you today?",
                "I'm here to assist you.",
                "Let me look into that for you."
            ]
        
        return suggestions[:3]  # Return top 3 suggestions


class DatabaseManager:
    """Secure database management"""
    
    def __init__(self, db_path: str = "whatsapp_context.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT,
                is_vip INTEGER DEFAULT 0,
                tags TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                last_contact TEXT,
                total_messages INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0.0,
                sentiment_history TEXT
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                content TEXT NOT NULL,
                direction TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                agent_id TEXT,
                category TEXT,
                sentiment TEXT,
                priority TEXT,
                metadata TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                status TEXT NOT NULL,
                amount REAL NOT NULL,
                items TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tracking_number TEXT,
                estimated_delivery TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)
        
        # Issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                issue_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                resolution TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_customer ON messages(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database initialized successfully")
    
    def save_customer(self, customer: Customer):
        """Save or update customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO customers 
            (customer_id, phone, name, email, is_vip, tags, notes, created_at, 
             last_contact, total_messages, avg_response_time, sentiment_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer.customer_id,
            customer.phone,
            customer.name,
            customer.email,
            1 if customer.is_vip else 0,
            json.dumps(customer.tags),
            customer.notes,
            customer.created_at,
            customer.last_contact,
            customer.total_messages,
            customer.avg_response_time,
            json.dumps(customer.sentiment_history)
        ))
        
        conn.commit()
        conn.close()
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Customer(
            customer_id=row[0],
            phone=row[1],
            name=row[2],
            email=row[3],
            is_vip=bool(row[4]),
            tags=json.loads(row[5]) if row[5] else [],
            notes=row[6] or "",
            created_at=row[7],
            last_contact=row[8],
            total_messages=row[9],
            avg_response_time=row[10],
            sentiment_history=json.loads(row[11]) if row[11] else []
        )
    
    def save_message(self, message: Message):
        """Save message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages 
            (message_id, customer_id, content, direction, timestamp, agent_id,
             category, sentiment, priority, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message.message_id,
            message.customer_id,
            message.content,
            message.direction,
            message.timestamp,
            message.agent_id,
            message.category.value if message.category else None,
            message.sentiment.value if message.sentiment else None,
            message.priority.value if message.priority else None,
            json.dumps(message.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_messages(self, customer_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages for a customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE customer_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (customer_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append(Message(
                message_id=row[0],
                customer_id=row[1],
                content=row[2],
                direction=row[3],
                timestamp=row[4],
                agent_id=row[5],
                category=MessageCategory(row[6]) if row[6] else None,
                sentiment=CustomerSentiment(row[7]) if row[7] else None,
                priority=MessagePriority(row[8]) if row[8] else None,
                metadata=json.loads(row[9]) if row[9] else {}
            ))
        
        return list(reversed(messages))  # Return in chronological order
    
    def save_order(self, order: Order):
        """Save order to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (order_id, customer_id, status, amount, items, created_at, updated_at,
             tracking_number, estimated_delivery, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id,
            order.customer_id,
            order.status,
            order.amount,
            json.dumps(order.items),
            order.created_at,
            order.updated_at,
            order.tracking_number,
            order.estimated_delivery,
            order.notes
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_orders(self, customer_id: str) -> List[Order]:
        """Get active orders for a customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM orders 
            WHERE customer_id = ? AND status NOT IN ('delivered', 'cancelled')
            ORDER BY created_at DESC
        """, (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        orders = []
        for row in rows:
            orders.append(Order(
                order_id=row[0],
                customer_id=row[1],
                status=row[2],
                amount=row[3],
                items=json.loads(row[4]),
                created_at=row[5],
                updated_at=row[6],
                tracking_number=row[7],
                estimated_delivery=row[8],
                notes=row[9] or ""
            ))
        
        return orders
    
    def get_last_issue(self, customer_id: str) -> Optional[Dict]:
        """Get last issue for customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM issues 
            WHERE customer_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (customer_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'issue_id': row[0],
            'customer_id': row[1],
            'category': row[2],
            'description': row[3],
            'status': row[4],
            'created_at': row[5],
            'resolved_at': row[6],
            'resolution': row[7]
        }


class ContextManager:
    """Main context management system"""
    
    def __init__(self, db_path: str = "whatsapp_context.db"):
        self.db = DatabaseManager(db_path)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.categorizer = MessageCategorizer()
        self.priority_calculator = PriorityCalculator(self.sentiment_analyzer)
        self.response_suggester = ResponseSuggester()
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def process_incoming_message(
        self,
        phone: str,
        message_content: str,
        agent_id: Optional[str] = None
    ) -> ContextSummary:
        """
        Process incoming WhatsApp message and return full context
        
        This is the main method agents will use
        """
        # Get or create customer
        customer = self.db.get_customer_by_phone(phone)
        if not customer:
            customer = self._create_new_customer(phone)
        
        # Analyze message
        sentiment = self.sentiment_analyzer.analyze(message_content)
        category = self.categorizer.categorize(message_content)
        priority = self.priority_calculator.calculate(
            message_content, customer, category, sentiment
        )
        
        # Create message record
        message = Message(
            message_id=str(uuid.uuid4()),
            customer_id=customer.customer_id,
            content=message_content,
            direction="inbound",
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            category=category,
            sentiment=sentiment,
            priority=priority
        )
        
        # Save message
        self.db.save_message(message)
        
        # Update customer
        customer.last_contact = message.timestamp
        customer.total_messages += 1
        customer.sentiment_history.append(sentiment.value)
        customer.sentiment_history = customer.sentiment_history[-10:]  # Keep last 10
        self.db.save_customer(customer)
        
        # Get context
        recent_messages = self.db.get_recent_messages(customer.customer_id, limit=10)
        active_orders = self.db.get_active_orders(customer.customer_id)
        last_issue = self.db.get_last_issue(customer.customer_id)
        
        # Generate insights
        key_insights = self._generate_insights(
            customer, recent_messages, active_orders, sentiment, category
        )
        
        # Generate warnings
        warnings = self._generate_warnings(
            customer, sentiment, priority, recent_messages
        )
        
        # Suggest responses
        suggested_responses = self.response_suggester.suggest(
            category, customer, recent_messages, active_orders
        )
        
        # Create context summary
        context = ContextSummary(
            customer=customer,
            recent_messages=recent_messages,
            active_orders=active_orders,
            last_issue=last_issue,
            suggested_responses=suggested_responses,
            priority=priority,
            sentiment=sentiment,
            key_insights=key_insights,
            warnings=warnings
        )
        
        self.logger.info(
            f"Processed message from {phone}: "
            f"Priority={priority.value}, Sentiment={sentiment.value}, "
            f"Category={category.value}"
        )
        
        return context
    
    def _create_new_customer(self, phone: str) -> Customer:
        """Create new customer record"""
        customer = Customer(
            customer_id=str(uuid.uuid4()),
            phone=phone
        )
        self.db.save_customer(customer)
        self.logger.info(f"Created new customer: {phone}")
        return customer
    
    def _generate_insights(
        self,
        customer: Customer,
        recent_messages: List[Message],
        active_orders: List[Order],
        sentiment: CustomerSentiment,
        category: MessageCategory
    ) -> List[str]:
        """Generate key insights for agent"""
        insights = []
        
        # Customer type insight
        if customer.is_vip:
            insights.append("🌟 VIP Customer - Prioritize response")
        
        # Message history insight
        if customer.total_messages == 1:
            insights.append("👋 First time contacting us")
        elif customer.total_messages > 20:
            insights.append(f"📊 Frequent customer ({customer.total_messages} messages)")
        
        # Order insight
        if active_orders:
            order = active_orders[0]
            insights.append(f"📦 Active Order: #{order.order_id} - {order.status}")
            if order.tracking_number:
                insights.append(f"🚚 Tracking: {order.tracking_number}")
            if order.estimated_delivery:
                insights.append(f"📅 Est. Delivery: {order.estimated_delivery}")
        
        # Sentiment trend
        if len(customer.sentiment_history) >= 3:
            recent_sentiments = customer.sentiment_history[-3:]
            if all(s in ['negative', 'very_negative'] for s in recent_sentiments):
                insights.append("⚠️ Customer has been consistently unhappy")
        
        # Response time expectation
        if customer.avg_response_time > 0:
            avg_mins = customer.avg_response_time / 60
            if avg_mins < 5:
                insights.append(f"⚡ Customer expects fast replies (~{avg_mins:.0f}min)")
        
        # Category-specific insights
        if category == MessageCategory.ORDER_STATUS and not active_orders:
            insights.append("ℹ️ Asking about order but no active orders found")
        
        return insights
    
    def _generate_warnings(
        self,
        customer: Customer,
        sentiment: CustomerSentiment,
        priority: MessagePriority,
        recent_messages: List[Message]
    ) -> List[str]:
        """Generate warnings for agent"""
        warnings = []
        
        # Critical priority warning
        if priority == MessagePriority.CRITICAL:
            warnings.append("🚨 CRITICAL: Requires immediate attention!")
        
        # Very negative sentiment warning
        if sentiment == CustomerSentiment.VERY_NEGATIVE:
            warnings.append("😡 Customer is very upset - handle with care")
        
        # Multiple recent contacts
        recent_count = len([m for m in recent_messages 
                           if m.direction == "inbound" and 
                           (datetime.now() - datetime.fromisoformat(m.timestamp)).seconds < 3600])
        if recent_count > 3:
            warnings.append(f"⏰ Customer messaged {recent_count} times in last hour")
        
        # No response to previous message
        if len(recent_messages) >= 2:
            last_two = recent_messages[-2:]
            if all(m.direction == "inbound" for m in last_two):
                warnings.append("💬 Previous message was not answered")
        
        return warnings
    
    def send_message(
        self,
        phone: str,
        message_content: str,
        agent_id: str
    ):
        """Record outbound message from agent"""
        customer = self.db.get_customer_by_phone(phone)
        if not customer:
            self.logger.warning(f"Attempted to send message to unknown customer: {phone}")
            return
        
        message = Message(
            message_id=str(uuid.uuid4()),
            customer_id=customer.customer_id,
            content=message_content,
            direction="outbound",
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id
        )
        
        self.db.save_message(message)
        self.logger.info(f"Recorded outbound message to {phone} by agent {agent_id}")
    
    def add_order(self, order: Order):
        """Add order to system"""
        self.db.save_order(order)
        self.logger.info(f"Added order {order.order_id} for customer {order.customer_id}")
    
    def update_customer_info(
        self,
        phone: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        is_vip: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None
    ):
        """Update customer information"""
        customer = self.db.get_customer_by_phone(phone)
        if not customer:
            self.logger.warning(f"Customer not found: {phone}")
            return
        
        if name is not None:
            customer.name = name
        if email is not None:
            customer.email = email
        if is_vip is not None:
            customer.is_vip = is_vip
        if tags is not None:
            customer.tags = tags
        if notes is not None:
            customer.notes = notes
        
        self.db.save_customer(customer)
        self.logger.info(f"Updated customer info for {phone}")
    
    def get_context_by_phone(self, phone: str) -> Optional[ContextSummary]:
        """Get current context for a phone number without new message"""
        customer = self.db.get_customer_by_phone(phone)
        if not customer:
            return None
        
        recent_messages = self.db.get_recent_messages(customer.customer_id, limit=10)
        active_orders = self.db.get_active_orders(customer.customer_id)
        last_issue = self.db.get_last_issue(customer.customer_id)
        
        # Get last message sentiment and category
        last_message = recent_messages[-1] if recent_messages else None
        sentiment = last_message.sentiment if last_message else CustomerSentiment.NEUTRAL
        category = last_message.category if last_message else MessageCategory.OTHER
        priority = last_message.priority if last_message else MessagePriority.NORMAL
        
        key_insights = self._generate_insights(
            customer, recent_messages, active_orders, sentiment, category
        )
        
        warnings = self._generate_warnings(
            customer, sentiment, priority, recent_messages
        )
        
        suggested_responses = self.response_suggester.suggest(
            category, customer, recent_messages, active_orders
        )
        
        return ContextSummary(
            customer=customer,
            recent_messages=recent_messages,
            active_orders=active_orders,
            last_issue=last_issue,
            suggested_responses=suggested_responses,
            priority=priority,
            sentiment=sentiment,
            key_insights=key_insights,
            warnings=warnings
        )
