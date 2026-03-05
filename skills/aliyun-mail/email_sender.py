#!/usr/bin/env python3
"""
Aliyun Mail Skill - Send emails via Aliyun Enterprise Mail
Supports plain text, Markdown (with syntax highlighting), and HTML emails with attachments.
"""

import smtplib
import os
import json
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import markdown
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight


class HighlightCodeExtension(markdown.extensions.Extension):
    """Custom extension to add syntax highlighting to code blocks"""
    
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(HighlightCodePreprocessor(md), 'highlight_code', 30)


class HighlightCodePreprocessor(markdown.preprocessors.Preprocessor):
    """Preprocessor to handle code blocks with syntax highlighting"""
    
    def run(self, lines):
        in_code_block = False
        current_language = None
        code_lines = []
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for code block start
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    language_match = line.strip()[3:].strip()
                    current_language = language_match if language_match else 'text'
                    code_lines = []
                    new_lines.append('')  # Placeholder for highlighted code
                else:
                    # End of code block
                    in_code_block = False
                    # Process the code block with syntax highlighting
                    if current_language and code_lines:
                        try:
                            lexer = get_lexer_by_name(current_language)
                            formatter = HtmlFormatter(style='default')
                            highlighted_code = highlight('\n'.join(code_lines), lexer, formatter)
                            # Replace the placeholder with highlighted code
                            new_lines[-1] = highlighted_code
                        except Exception:
                            # Fallback to plain code block
                            code_html = '<pre><code>' + '\n'.join(code_lines) + '</code></pre>'
                            new_lines[-1] = code_html
                    current_language = None
                    code_lines = []
            elif in_code_block:
                code_lines.append(line)
            else:
                new_lines.append(line)
            
            i += 1
        
        return new_lines


def load_config(config_path=None):
    """
    Load SMTP configuration from file.
    Default path: ~/.openclaw/smtp-config.json
    """
    if config_path is None:
        config_path = os.path.expanduser("~/.openclaw/smtp-config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"SMTP configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def create_attachment(filepath):
    """Create attachment from file"""
    with open(filepath, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {os.path.basename(filepath)}'
    )
    return part


def send_email(to_email, subject, body=None, body_file=None, body_type='plain', 
               attachments=None, config_path=None):
    """
    Send email with specified content type
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str, optional): Email body content
        body_file (str, optional): Path to file containing email body
        body_type (str): 'plain', 'markdown', or 'html'
        attachments (list, optional): List of file paths to attach
        config_path (str, optional): Path to SMTP config file
    """
    # Load configuration
    config = load_config(config_path)
    
    # Validate inputs
    if not body and not body_file:
        raise ValueError("Either body or body_file must be provided")
    
    if body_file and not os.path.exists(body_file):
        raise FileNotFoundError(f"Body file not found: {body_file}")
    
    # Read body from file if provided
    if body_file:
        with open(body_file, 'r') as f:
            body = f.read()
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = config.get('emailFrom', config['username'])
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Add body based on type
    if body_type == 'html':
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    elif body_type == 'markdown':
        # Convert Markdown to HTML with syntax highlighting
        html_body = markdown.markdown(
            body, 
            extensions=[HighlightCodeExtension(), 'fenced_code']
        )
        # Add CSS for styling
        full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                h1, h2, h3 {{ color: #333; }}
                .highlight {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
            </style>
            <style>
                {HtmlFormatter().get_style_defs('.highlight')}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """
        msg.attach(MIMEText(full_html, 'html', 'utf-8'))
    else:  # plain text
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Add attachments
    if attachments:
        for filepath in attachments:
            if os.path.exists(filepath):
                msg.attach(create_attachment(filepath))
            else:
                print(f"Warning: Attachment file not found: {filepath}", file=sys.stderr)
    
    # Send email
    try:
        if config.get('useTLS', False):
            server = smtplib.SMTP_SSL(config['server'], config['port'])
        else:
            server = smtplib.SMTP(config['server'], config['port'])
            if config.get('startTLS', False):
                server.starttls()
        
        server.login(config['username'], config['password'])
        text = msg.as_string()
        server.sendmail(msg['From'], to_email, text)
        server.quit()
        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Send email via Aliyun Enterprise Mail")
    parser.add_argument('--to', required=True, help="Recipient email address")
    parser.add_argument('--subject', required=True, help="Email subject")
    parser.add_argument('--body', help="Email body content")
    parser.add_argument('--body-file', help="Path to file containing email body")
    parser.add_argument('--type', choices=['plain', 'markdown', 'html'], 
                       default='plain', help="Email body type (default: plain)")
    parser.add_argument('--attachments', nargs='*', help="File paths to attach")
    parser.add_argument('--config', help="Path to SMTP config file")
    
    args = parser.parse_args()
    
    try:
        success = send_email(
            to_email=args.to,
            subject=args.subject,
            body=args.body,
            body_file=args.body_file,
            body_type=args.type,
            attachments=args.attachments,
            config_path=args.config
        )
        if success:
            print("✅ Email sent successfully!")
            return 0
        else:
            print("❌ Failed to send email", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())