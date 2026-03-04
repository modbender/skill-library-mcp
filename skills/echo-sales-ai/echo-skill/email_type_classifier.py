"""
Echo - AI-powered sales email generation and CRM system
Standalone service with Telegram integration
"""

import os
import yaml
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import pickle
import base64
from bs4 import BeautifulSoup

# Telegram imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Google Gmail imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Import the agents
from agents.email_type_classifier import EmailTypeClassifier
from agents.feedback_interpreter import FeedbackInterpreter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'
)
logger = logging.getLogger(__name__)

class EchoService:
    def __init__(self, config_path=\'config.yaml\'):
        """Initialize Echo service"""
        self.config = self.load_config(config_path)
        self.db_path = self.config[\"config\"][\"database_path\"]
        self.credentials_path = os.path.expanduser(self.config[\"config\"][\"credentials_path\"])
        self.telegram_token = self.config[\"config\"][\"telegram_token\"]
        self.token_path = self.config[\"config\\"].get(\'token_path\', \'./data/token.pickle\')
        self.openai_api_key = self.config[\"config\"][\"openai_api_key\"]
        
        # Initialize database
        self.init_database()
        
        # Initialize Gmail service (lazy load)
        self.gmail_service = None

        # Initialize agents
        self.email_classifier = EmailTypeClassifier()
        self.feedback_interpreter = FeedbackInterpreter(api_key=self.openai_api_key)
        
        logger.info("Echo service initialized successfully!")
    
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, \'r\') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def init_database(self):
        """Initialize SQLite database for CRM"""
        # ... (database code remains the same) ...
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(\'\\'\'
                CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT UNIQUE, website TEXT, industry TEXT, location TEXT, size TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            \\'\\'\')
            cursor.execute(\'\\'\'
                CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, company_id INTEGER, name TEXT, email TEXT UNIQUE, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (company_id) REFERENCES companies(id))
            \\'\\'\')
            cursor.execute(\'\\'\'
                CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, contact_id INTEGER, company_id INTEGER, product TEXT, price REAL, currency TEXT, date_sent TIMESTAMP, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (contact_id) REFERENCES contacts(id), FOREIGN KEY (company_id) REFERENCES companies(id))
            \\'\\'\')
            cursor.execute(\'\\'\'
                CREATE TABLE IF NOT EXISTS email_threads (id INTEGER PRIMARY KEY, contact_id INTEGER, subject TEXT, last_message TIMESTAMP, stage TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (contact_id) REFERENCES contacts(id))
            \\'\\'\')
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_gmail_service(self):
        # ... (gmail service code remains the same) ...
        if self.gmail_service:
            return self.gmail_service
        try:
            SCOPES = [\'https://www.googleapis.com/auth/gmail.readonly\', \'https://www.googleapis.com/auth/gmail.send\']
            creds = None
            if os.path.exists(self.token_path ):
                with open(self.token_path, \'rb\') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(self.token_path, \'wb\') as token:
                    pickle.dump(creds, token)
            self.gmail_service = googleapiclient.discovery.build(\'gmail\', \'v1\', credentials=creds)
            logger.info("Gmail service authenticated successfully")
            return self.gmail_service
        except Exception as e:
            logger.error(f"Failed to authenticate Gmail: {e}")
            return None

    def get_email_body(self, msg_id):
        # ... (get email body code remains the same) ...
        service = self.get_gmail_service()
        if not service:
            return ""
        message = service.users().messages().get(userId=\'me\', id=msg_id, format=\'full\').execute()
        payload = message.get(\'payload\', {})
        parts = payload.get(\'parts\', [])
        body = ""
        if \'data\' in payload[\'body\
        ]:
            data = payload[\'body\\[\'data\']
            body = base64.urlsafe_b64decode(data).decode(\'utf-8\')
        elif parts:
            for part in parts:
                if part[\'mimeType\'] == \'text/plain\':
                    data = part[\'body\\'].get(\'data\')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode(\'utf-8\')
                        break
        return body

    def fetch_recent_emails(self, max_results=10):
        # ... (fetch recent emails code remains the same) ...
        try:
            service = self.get_gmail_service()
            if not service:
                return []
            results = service.users().messages().list(userId=\'me\', maxResults=max_results).execute()
            messages = results.get(\'messages\', [])
            email_details = []
            for msg in messages:
                email_body = self.get_email_body(msg[\'id\'])
                email_type = self.email_classifier.classify(email_body)
                email_details.append({\'id\': msg[\'id\'], \'type\': email_type})
            logger.info(f"Fetched and classified {len(email_details)} recent emails")
            return email_details
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Echo is running!\n\n"
        "Available commands:\n"
        "/status - Check Echo status\n"
        "/emails - Fetch and classify recent emails\n"
        "/classify [text] - Classify a piece of text\n"
        "/feedback [text] - Give feedback on an email\n"
        "/help - Show all commands"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Echo is running and ready!\n\n"
        "Status:\n"
        "- Gmail: Connected\n"
        "- Database: Active\n"
        "- Telegram: Connected"
    )

async def emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (emails command remains the same) ...
    echo_service = context.bot_data.get(\'echo_service\')
    if not echo_service:
        await update.message.reply_text("❌ Echo service not initialized")
        return
    await update.message.reply_text("Fetching and classifying recent emails...")
    email_details = echo_service.fetch_recent_emails(5)
    if not email_details:
        await update.message.reply_text("No recent emails found")
        return
    response = f"📧 Found and classified {len(email_details)} recent emails\n\n"
    for i, detail in enumerate(email_details, 1):
        response += f"{i}. ID: {detail[\'id\']} - Type: {detail[\'type\']}\n"
    await update.message.reply_text(response)

async def classify_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (classify_text command remains the same) ...
    echo_service = context.bot_data.get(\'echo_service\')
    if not echo_service:
        await update.message.reply_text("❌ Echo service not initialized")
        return
    text_to_classify = \' \'.join(context.args)
    if not text_to_classify:
        await update.message.reply_text("Please provide text to classify. Usage: /classify [text]")
        return
    classification = echo_service.email_classifier.classify(text_to_classify)
    await update.message.reply_text(f"Classification: {classification}")

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interpret natural language feedback"""
    echo_service = context.bot_data.get(\'echo_service\')
    if not echo_service:
        await update.message.reply_text("❌ Echo service not initialized")
        return

    feedback_text = \' \'.join(context.args)
    if not feedback_text:
        await update.message.reply_text("Please provide feedback. Usage: /feedback [your feedback here]")
        return

    await update.message.reply_text("Interpreting your feedback...")
    interpretation = echo_service.feedback_interpreter.interpret(feedback_text)
    
    # Pretty print the JSON response
    pretty_interpretation = json.dumps(json.loads(interpretation), indent=2)
    
    await update.message.reply_text(f"Feedback Interpretation:\n```json\n{pretty_interpretation}\n```")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Echo - AI Sales Assistant\n\n"
        "Commands:\n"
        "/start - Start Echo\n"
        "/status - Check status\n"
        "/emails - Fetch and classify recent emails\n"
        "/classify [text] - Classify a piece of text\n"
        "/feedback [text] - Give feedback on an email\n"
        "/help - Show this help"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (handle_message remains the same) ...
    user_message = update.message.text
    if user_message.startswith(\'/\'):
        return
    await update.message.reply_text(f"Echo received: {user_message}")

def main():
    """Main function to run Echo service"""
    echo_service = EchoService()
    app = Application.builder().token(echo_service.telegram_token).build()
    app.bot_data[\'echo_service\'] = echo_service
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("emails", emails))
    app.add_handler(CommandHandler("classify", classify_text))
    app.add_handler(CommandHandler("feedback", feedback)) # <-- NEW HANDLER
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Echo service starting...")
    logger.info("Telegram bot is polling for messages...")
    app.run_polling()

if __name__ == \'__main__\':
    main()
