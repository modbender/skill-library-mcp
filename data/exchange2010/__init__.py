"""
Exchange 2010 EWS Integration
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Fix timezone warnings
from exchangelib.winzone import MS_TIMEZONE_TO_IANA_MAP, CLDR_TO_MS_TIMEZONE_MAP
MS_TIMEZONE_TO_IANA_MAP['(GMT+01:00) Belgrad, Bratislava, Budapest, Ljubljana, Prag'] = "Europe/Vienna"
MS_TIMEZONE_TO_IANA_MAP['(no TZ description)'] = "Europe/Vienna"
MS_TIMEZONE_TO_IANA_MAP[''] = "Europe/Vienna"

def _load_env():
    """Load credentials from .env.credentials"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.credentials')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val

def get_account():
    """Get authenticated Exchange account"""
    from exchangelib import Credentials, Account, Configuration, NTLM, DELEGATE
    from exchangelib.version import Version, EXCHANGE_2010_SP2
    
    _load_env()
    
    domain = os.getenv('EXCHANGE_DOMAIN', 'friendly-it')
    username = os.getenv('PICARD_USERNAME', 'picard')
    email = os.getenv('EXCHANGE_EMAIL', 'picard@friendly-it.com')
    password = os.getenv('PICARD_PASSWORD')
    server = os.getenv('EXCHANGE_SERVER', 'oberau.friendly-it.at')
    
    if not password:
        raise ValueError("EXCHANGE_PASSWORD not found in .env.credentials")
    
    creds = Credentials(username=f"{domain}\\{username}", password=password)
    config = Configuration(
        server=server,
        credentials=creds,
        auth_type=NTLM,
        version=Version(EXCHANGE_2010_SP2)
    )
    
    return Account(
        primary_smtp_address=email,
        config=config,
        autodiscover=False,
        access_type=DELEGATE
    )

def get_inbox(account):
    """Get inbox folder"""
    return account.inbox

def get_calendar(account):
    """Get calendar folder"""
    return account.calendar

def get_unread_emails(account, limit: int = 50) -> List[Dict[str, Any]]:
    """Get unread emails from inbox"""
    emails = []
    for item in account.inbox.filter(is_read=False).order_by('-datetime_received')[:limit]:
        emails.append({
            'id': item.id,
            'subject': item.subject,
            'sender': str(item.sender.email_address) if item.sender else None,
            'received': item.datetime_received,
            'body': item.body,
            'is_read': item.is_read
        })
    return emails

def get_calendar_events(account, start_date: datetime = None, end_date: datetime = None):
    """Get calendar events for date range"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date + timedelta(days=1)
    
    # Convert date to EWSDateTime with timezone if needed
    if hasattr(start_date, 'year') and not hasattr(start_date, 'hour'):
        start_date = EWSDateTime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    if hasattr(end_date, 'year') and not hasattr(end_date, 'hour'):
        end_date = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    events = []
    for item in account.calendar.view(start=start_date, end=end_date):
        events.append({
            'id': item.id,
            'subject': item.subject,
            'start': item.start,
            'end': item.end,
            'body': item.body,
            'location': item.location
        })
    return events

def create_calendar_event(
    subject: str,
    start: datetime,
    end: datetime,
    body: str = "",
    location: str = ""
):
    """Create a new calendar event"""
    from exchangelib.items import CalendarItem
    
    account = get_account()
    
    item = CalendarItem(
        account=account,
        folder=account.calendar,
        subject=subject,
        start=start,
        end=end,
        body=body,
        location=location
    )
    item.save()
    return item.id

def send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: List[str] = None,
    bcc: List[str] = None
):
    """Send an email"""
    from exchangelib import Message, Mailbox
    
    account = get_account()
    
    to_recipients = [Mailbox(email_address=e) for e in to]
    cc_recipients = [Mailbox(email_address=e) for e in (cc or [])]
    bcc_recipients = [Mailbox(email_address=e) for e in (bcc or [])]
    
    msg = Message(
        account=account,
        folder=account.sent,
        subject=subject,
        body=body,
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
        bcc_recipients=bcc_recipients
    )
    msg.send_and_save()
    return msg.id

def get_shared_calendar(account, email_address: str):
    """Get a shared/delegate calendar from another user"""
    from exchangelib.folders import Calendar
    from exchangelib.account import Account
    from exchangelib import Credentials, Configuration, NTLM, DELEGATE
    from exchangelib.version import Version, EXCHANGE_2010_SP2
    
    _load_env()
    
    domain = os.getenv('EXCHANGE_DOMAIN', 'friendly-it')
    username = os.getenv('PICARD_USERNAME', 'picard')
    password = os.getenv('PICARD_PASSWORD')
    server = os.getenv('EXCHANGE_SERVER', 'oberau.friendly-it.at')
    
    # Create credentials for accessing shared calendar
    creds = Credentials(username=f"{domain}\\{username}", password=password)
    config = Configuration(
        server=server,
        credentials=creds,
        auth_type=NTLM,
        version=Version(EXCHANGE_2010_SP2)
    )
    
    # Access the shared account with delegate permissions
    shared_account = Account(
        primary_smtp_address=email_address,
        config=config,
        autodiscover=False,
        access_type=DELEGATE
    )
    
    return shared_account.calendar

def get_shared_calendar_events(
    email_address: str,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get events from a shared calendar"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    
    account = get_account()
    calendar = get_shared_calendar(account, email_address)
    
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date + timedelta(days=1)
    
    # Convert date to EWSDateTime with timezone if needed
    if hasattr(start_date, 'year') and not hasattr(start_date, 'hour'):
        start_date = EWSDateTime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    if hasattr(end_date, 'year') and not hasattr(end_date, 'hour'):
        end_date = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    events = []
    for item in calendar.view(start=start_date, end=end_date):
        events.append({
            'id': item.id,
            'subject': item.subject,
            'start': item.start,
            'end': item.end,
            'body': item.body,
            'location': item.location
        })
    return events

def search_calendar_events(
    email_address: str,
    search_term: str,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Search calendar events by keyword"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    
    account = get_account()
    calendar = get_shared_calendar(account, email_address)
    
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = start_date + timedelta(days=365)
    
    # Convert date to EWSDateTime with timezone if needed
    if hasattr(start_date, 'year') and not hasattr(start_date, 'hour'):
        start_date = EWSDateTime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    if hasattr(end_date, 'year') and not hasattr(end_date, 'hour'):
        end_date = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    search_lower = search_term.lower()
    events = []
    
    for item in calendar.view(start=start_date, end=end_date):
        subject = (item.subject or '').lower()
        body = (item.body or '').lower()
        if search_lower in subject or search_lower in body:
            events.append({
                'id': item.id,
                'subject': item.subject,
                'start': item.start,
                'end': item.end,
                'body': item.body,
                'location': item.location
            })
    return events

def count_ekadashi_events(email_address: str, start_year: int = 2025):
    """Count Ekadashi events in a shared calendar from start_year to today"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    from datetime import date
    
    account = get_account()
    calendar = get_shared_calendar(account, email_address)
    
    start = EWSDateTime(start_year, 1, 1, tzinfo=UTC)
    end = EWSDateTime(date.today().year, date.today().month, date.today().day + 1, tzinfo=UTC)
    
    count = 0
    events = []
    
    # Use filter with subject contains for efficient search
    try:
        # Search for 'ekadashi' in subject
        for item in calendar.filter(
            start__gte=start,
            end__lte=end,
            subject__contains='Ekadashi'
        ):
            count += 1
            events.append({
                'date': item.start.strftime('%Y-%m-%d'),
                'subject': item.subject
            })
    except Exception as e:
        print(f"Warning: Error searching with filter: {e}")
    
    return count, events

def search_calendar_by_subject(
    email_address: str,
    search_term: str,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Search calendar events by subject using EWS filter (case-insensitive)"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    from datetime import date
    
    account = get_account()
    calendar = get_shared_calendar(account, email_address)
    
    if start_date is None:
        start_date = EWSDateTime(2025, 1, 1, tzinfo=UTC)
    if end_date is None:
        end_date = EWSDateTime(date.today().year, date.today().month, date.today().day + 1, tzinfo=UTC)
    
    # Convert dates if needed
    if hasattr(start_date, 'year') and not hasattr(start_date, 'hour'):
        start_date = EWSDateTime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    if hasattr(end_date, 'year') and not hasattr(end_date, 'hour'):
        end_date = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    events = []
    
    try:
        # Use EWS filter for subject search (much faster than iterating all events)
        for item in calendar.filter(
            start__gte=start_date,
            end__lte=end_date,
            subject__contains=search_term
        ):
            events.append({
                'id': item.id,
                'subject': item.subject,
                'start': item.start,
                'end': item.end,
                'location': item.location
            })
    except Exception as e:
        print(f"Filter search failed, falling back to view: {e}")
        # Fallback to view with manual filtering
        for item in calendar.view(start=start_date, end=end_date):
            if search_term.lower() in (item.subject or '').lower():
                events.append({
                    'id': item.id,
                    'subject': item.subject,
                    'start': item.start,
                    'end': item.end,
                    'location': item.location
                })
    
    return events

def get_today_events(email_address: str = None) -> List[Dict[str, Any]]:
    """Get today's calendar events"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    from datetime import date, timedelta
    
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    today = date.today()
    start = EWSDateTime(today.year, today.month, today.day, tzinfo=UTC)
    end = EWSDateTime(today.year, today.month, today.day + 1, tzinfo=UTC)
    
    events = []
    for item in calendar.view(start=start, end=end).order_by('start'):
        events.append({
            'id': item.id,
            'subject': item.subject,
            'start': item.start,
            'end': item.end,
            'location': item.location,
            'body': item.body
        })
    return events

def get_upcoming_events(email_address: str = None, days: int = 7) -> List[Dict[str, Any]]:
    """Get upcoming events for the next N days"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    from datetime import datetime, timedelta
    
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    now = datetime.now()
    start = EWSDateTime(now.year, now.month, now.day, tzinfo=UTC)
    end_date = now + timedelta(days=days)
    end = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    events = []
    for item in calendar.view(start=start, end=end).order_by('start'):
        events.append({
            'id': item.id,
            'subject': item.subject,
            'start': item.start,
            'end': item.end,
            'location': item.location
        })
    return events

def get_event_details(event_id: str, email_address: str = None) -> Dict[str, Any]:
    """Get detailed information about a specific calendar event"""
    from exchangelib import Account
    
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    try:
        # Get item by ID
        item = account.fetch(ids=[event_id])[0]
        return {
            'id': item.id,
            'subject': item.subject,
            'start': item.start,
            'end': item.end,
            'location': item.location,
            'body': item.body,
            'organizer': str(item.organizer.email_address) if item.organizer else None,
            'required_attendees': [str(a.mailbox.email_address) for a in item.required_attendees] if item.required_attendees else [],
            'optional_attendees': [str(a.mailbox.email_address) for a in item.optional_attendees] if item.optional_attendees else [],
            'is_recurring': item.is_recurring,
            'sensitivity': item.sensitivity,
            'categories': item.categories
        }
    except Exception as e:
        return {'error': str(e)}

def delete_calendar_event(event_id: str, email_address: str = None) -> bool:
    """Delete a calendar event by ID"""
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    try:
        # Get and delete the item
        for item in calendar.filter(id=event_id):
            item.delete()
            return True
        return False
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False

def list_available_calendars(account) -> List[Dict[str, str]]:
    """List all available calendars in the account"""
    calendars = []
    for folder in account.root.walk():
        folder_type = folder.__class__.__name__
        if folder_type == 'Calendar':
            calendars.append({
                'name': folder.name,
                'id': folder.id,
                'total_count': getattr(folder, 'total_count', 'N/A')
            })
    return calendars

def mark_email_as_read(email_id: str) -> bool:
    """Mark an email as read by ID"""
    account = get_account()
    try:
        for item in account.inbox.filter(id=email_id):
            item.is_read = True
            item.save()
            return True
        return False
    except Exception as e:
        print(f"Error marking email as read: {e}")
        return False

def search_contacts(search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search contacts in the global address list (GAL) or local contacts"""
    account = get_account()
    contacts = []
    
    try:
        # Search in local contacts folder
        for contact in account.contacts.filter(
            display_name__contains=search_term
        )[:limit]:
            contacts.append({
                'id': contact.id,
                'name': contact.display_name,
                'email': contact.email_addresses[0].email if contact.email_addresses else None,
                'phone': contact.phone_numbers[0].phone_number if contact.phone_numbers else None,
                'company': contact.company_name,
                'department': contact.department
            })
    except Exception as e:
        print(f"Error searching contacts: {e}")
    
    return contacts

def resolve_name(name: str) -> Optional[Dict[str, str]]:
    """Resolve a name to email address (GAL lookup)"""
    account = get_account()
    
    try:
        from exchangelib.services import ResolveNames
        from exchangelib.properties import Mailbox
        
        # Use ResolveNames service for GAL lookup
        results = list(ResolveNames(protocol=account.protocol).call(unresolved_entries=[name]))
        
        if results:
            result = results[0]
            return {
                'name': result.contact.display_name if result.contact else name,
                'email': result.mailbox.email_address if result.mailbox else None,
                'resolution_type': result.resolution_type
            }
    except Exception as e:
        print(f"Error resolving name: {e}")
    
    return None

def process_attachment_content(email_id: str, attachment_name: str = None) -> List[Dict[str, Any]]:
    """Process attachment content - extract text from PDFs, images, etc."""
    import tempfile
    import os
    
    account = get_account()
    results = []
    
    try:
        for item in account.inbox.filter(id=email_id):
            if not hasattr(item, 'attachments') or not item.attachments:
                return []
            
            for attachment in item.attachments:
                if attachment_name and attachment.name != attachment_name:
                    continue
                
                result = {
                    'name': attachment.name,
                    'content_type': attachment.content_type,
                    'size': len(attachment.content) if hasattr(attachment, 'content') else 0
                }
                
                # Save to temp file for processing
                if hasattr(attachment, 'content'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment.name)[1]) as tmp:
                        tmp.write(attachment.content)
                        tmp_path = tmp.name
                    
                    result['temp_path'] = tmp_path
                    
                    # Try to extract text content based on file type
                    content_type = (attachment.content_type or '').lower()
                    
                    if 'pdf' in content_type or attachment.name.endswith('.pdf'):
                        result['extracted_text'] = _extract_pdf_text(tmp_path)
                    elif 'text' in content_type or any(attachment.name.endswith(ext) for ext in ['.txt', '.csv', '.json']):
                        try:
                            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                                result['extracted_text'] = f.read()
                        except Exception as e:
                            result['extraction_error'] = str(e)
                    elif 'image' in content_type:
                        result['note'] = 'Image attachment - use vision model for OCR'
                    
                    results.append(result)
            
            break
    except Exception as e:
        print(f"Error processing attachments: {e}")
    
    return results

def _extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        # Try PyPDF2 first
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except ImportError:
        pass
    
    try:
        # Try pdfplumber as alternative
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except ImportError:
        return "PDF text extraction requires PyPDF2 or pdfplumber: pip install PyPDF2"
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def get_tasks(status: str = None, folder: str = 'tasks') -> List[Dict[str, Any]]:
    """Get tasks/to-do items from Exchange"""
    account = get_account()
    tasks = []
    
    try:
        # Get tasks folder
        tasks_folder = account.tasks
        
        query = tasks_folder.all()
        if status:
            query = query.filter(status=status)
        
        for task in query.order_by('-datetime_created'):
            tasks.append({
                'id': task.id,
                'subject': task.subject,
                'body': task.body,
                'status': task.status,
                'percent_complete': task.percent_complete,
                'start_date': task.start_date,
                'due_date': task.due_date,
                'is_complete': task.is_complete,
                'importance': task.importance,
                'categories': task.categories
            })
    except Exception as e:
        print(f"Error getting tasks: {e}")
    
    return tasks

def create_task(
    subject: str,
    body: str = "",
    due_date: datetime = None,
    importance: str = "Normal",
    categories: List[str] = None
) -> str:
    """Create a new task/to-do item"""
    from exchangelib.items import Task
    
    account = get_account()
    
    task = Task(
        account=account,
        folder=account.tasks,
        subject=subject,
        body=body,
        due_date=due_date,
        importance=importance,
        categories=categories or []
    )
    task.save()
    return task.id

def complete_task(task_id: str) -> bool:
    """Mark a task as complete"""
    account = get_account()
    
    try:
        for task in account.tasks.filter(id=task_id):
            task.is_complete = True
            task.percent_complete = 100
            task.status = 'Completed'
            task.save()
            return True
        return False
    except Exception as e:
        print(f"Error completing task: {e}")
        return False

def delete_task(task_id: str) -> bool:
    """Delete a task"""
    account = get_account()
    
    try:
        for task in account.tasks.filter(id=task_id):
            task.delete()
            return True
        return False
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def get_email_attachments(email_id: str, download_path: str = None) -> List[Dict[str, Any]]:
    """Get attachments from an email"""
    account = get_account()
    attachments = []
    
    try:
        # Get the email item
        for item in account.inbox.filter(id=email_id):
            if not hasattr(item, 'attachments') or not item.attachments:
                return []
            
            for attachment in item.attachments:
                att_info = {
                    'name': attachment.name,
                    'content_type': attachment.content_type,
                    'size': len(attachment.content) if hasattr(attachment, 'content') else 0,
                    'is_inline': getattr(attachment, 'is_inline', False)
                }
                
                # Download if path provided
                if download_path and hasattr(attachment, 'content'):
                    import os
                    os.makedirs(download_path, exist_ok=True)
                    file_path = os.path.join(download_path, attachment.name)
                    with open(file_path, 'wb') as f:
                        f.write(attachment.content)
                    att_info['downloaded_path'] = file_path
                
                attachments.append(att_info)
            
            break
    except Exception as e:
        print(f"Error getting attachments: {e}")
    
    return attachments

def search_emails(
    search_term: str = None,
    sender: str = None,
    subject: str = None,
    is_unread: bool = None,
    folder: str = 'inbox',
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Search emails with various filters"""
    account = get_account()
    
    # Get the folder
    if folder.lower() == 'inbox':
        search_folder = account.inbox
    elif folder.lower() == 'sent':
        search_folder = account.sent
    elif folder.lower() == 'drafts':
        search_folder = account.drafts
    else:
        # Try to find by name
        search_folder = account.inbox
        for f in account.root.walk():
            if folder.lower() in f.name.lower():
                search_folder = f
                break
    
    # Build query
    query = search_folder.all()
    
    if search_term:
        query = query.filter(body__contains=search_term)
    if sender:
        query = query.filter(sender__icontains=sender)
    if subject:
        query = query.filter(subject__contains=subject)
    if is_unread is not None:
        query = query.filter(is_read=not is_unread)
    
    emails = []
    for item in query.order_by('-datetime_received')[:limit]:
        emails.append({
            'id': item.id,
            'subject': item.subject,
            'sender': str(item.sender.email_address) if item.sender else None,
            'received': item.datetime_received,
            'is_read': item.is_read,
            'has_attachments': item.has_attachments,
            'importance': item.importance
        })
    
    return emails

def update_calendar_event(
    event_id: str,
    subject: str = None,
    start: datetime = None,
    end: datetime = None,
    body: str = None,
    location: str = None,
    email_address: str = None
) -> bool:
    """Update an existing calendar event"""
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    try:
        for item in calendar.filter(id=event_id):
            if subject is not None:
                item.subject = subject
            if start is not None:
                item.start = start
            if end is not None:
                item.end = end
            if body is not None:
                item.body = body
            if location is not None:
                item.location = location
            item.save()
            return True
        return False
    except Exception as e:
        print(f"Error updating event: {e}")
        return False

def get_recurring_events(
    email_address: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    days: int = None
) -> List[Dict[str, Any]]:
    """Get recurring/series events"""
    from exchangelib import EWSDateTime
    from exchangelib.ewsdatetime import UTC
    
    account = get_account()
    
    if email_address:
        calendar = get_shared_calendar(account, email_address)
    else:
        calendar = account.calendar
    
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        if days is not None:
            end_date = start_date + timedelta(days=days)
        else:
            end_date = start_date + timedelta(days=30)
    
    # Convert to EWSDateTime with timezone
    if not isinstance(start_date, EWSDateTime):
        start_date = EWSDateTime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    if not isinstance(end_date, EWSDateTime):
        end_date = EWSDateTime(end_date.year, end_date.month, end_date.day, tzinfo=UTC)
    
    recurring = []
    for item in calendar.view(start=start_date, end=end_date):
        if item.is_recurring:
            recurring.append({
                'id': item.id,
                'subject': item.subject,
                'start': item.start,
                'end': item.end,
                'location': item.location,
                'recurrence': str(item.recurrence) if item.recurrence else 'Unknown pattern'
            })
    
    return recurring

def get_folder_emails(
    folder_name: str = 'inbox',
    limit: int = 50,
    is_unread: bool = None
) -> List[Dict[str, Any]]:
    """Get emails from specific folder (sent, drafts, trash, etc.)"""
    account = get_account()
    
    # Map common folder names
    folder_map = {
        'inbox': account.inbox,
        'sent': account.sent,
        'drafts': account.drafts,
        'trash': account.trash,
        'junk': account.junk,
        'outbox': account.outbox,
    }
    
    folder = folder_map.get(folder_name.lower())
    
    if not folder:
        # Try to find by walking folders
        for f in account.root.walk():
            if folder_name.lower() in f.name.lower():
                folder = f
                break
    
    if not folder:
        return []
    
    query = folder.all()
    if is_unread is not None:
        query = query.filter(is_read=not is_unread)
    
    emails = []
    for item in query.order_by('-datetime_received')[:limit]:
        emails.append({
            'id': item.id,
            'subject': item.subject,
            'sender': str(item.sender.email_address) if item.sender else None,
            'received': item.datetime_received,
            'is_read': item.is_read,
            'folder': folder.name
        })
    
    return emails

def list_email_folders(account) -> List[Dict[str, str]]:
    """List all email folders in the account"""
    folders = []
    for folder in account.root.walk():
        folder_type = folder.__class__.__name__
        if folder_type in ['Inbox', 'SentItems', 'Drafts', 'Trash', 'JunkEmail', 'Messages']:
            folders.append({
                'name': folder.name,
                'type': folder_type,
                'id': folder.id,
                'total_count': getattr(folder, 'total_count', 'N/A'),
                'unread_count': getattr(folder, 'unread_count', 'N/A')
            })
    return folders

def get_out_of_office(email_address: str = None) -> Dict[str, Any]:
    """Get Out of Office settings"""
    account = get_account()
    
    try:
        oof = account.oof_settings
        
        # Handle different OOF states
        is_enabled = oof.state == 'Enabled' if hasattr(oof, 'state') else bool(getattr(oof, 'internal_reply', None))
        
        return {
            'enabled': is_enabled,
            'state': getattr(oof, 'state', 'Unknown'),
            'start': getattr(oof, 'start', None),
            'end': getattr(oof, 'end', None),
            'internal_reply': getattr(oof, 'internal_reply', None),
            'external_reply': getattr(oof, 'external_reply', None),
            'external_audience': getattr(oof, 'external_audience', None)  # 'All', 'Known', or 'None'
        }
    except Exception as e:
        return {'error': str(e)}

def set_out_of_office(
    enabled: bool,
    internal_reply: str,
    external_reply: str = None,
    start: datetime = None,
    end: datetime = None,
    external_audience: str = 'All'
) -> bool:
    """Set Out of Office message"""
    account = get_account()
    
    try:
        from exchangelib.settings import OofSettings
        
        oof = OofSettings(
            enabled=enabled,
            internal_reply=internal_reply,
            external_reply=external_reply or internal_reply,
            start=start,
            end=end,
            external_audience=external_audience  # 'All', 'Known', 'None'
        )
        
        account.oof_settings = oof
        return True
    except Exception as e:
        print(f"Error setting OOF: {e}")
        return False

if __name__ == '__main__':
    # Test
    account = get_account()
    print(f"✅ Connected to Exchange 2010")
    print(f"📧 Inbox: {account.inbox.name}")
    print(f"📅 Calendar: {account.calendar.name}")
