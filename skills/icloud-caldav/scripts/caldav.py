#!/usr/bin/env python3
"""
iCloud CalDAV CLI - Python rewrite
Direct access to iCloud Calendar via CalDAV protocol
"""

import os
import sys
import re
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests")
    sys.exit(1)

try:
    from icalendar import Calendar, Event
except ImportError:
    print("Warning: 'icalendar' not installed. Install with: pip install icalendar")
    Calendar = None
    Event = None

# XML namespaces
NS = {
    'D': 'DAV:',
    'cal': 'urn:ietf:params:xml:ns:caldav',
    'cs': 'http://calendarserver.org/ns/'
}

# Register namespaces for ElementTree
for prefix, uri in NS.items():
    ET.register_namespace(prefix if prefix != 'D' else '', uri)


class iCloudCalDAV:
    """iCloud CalDAV client"""
    
    def __init__(self, apple_id: str, app_password: str):
        self.apple_id = apple_id
        self.app_password = app_password
        self.auth = HTTPBasicAuth(apple_id, app_password)
        self.base_url = "https://caldav.icloud.com"
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8'
        })
        self._principal = None
        self._calendar_home = None
    
    def _request(self, method: str, url: str, body: str = None, depth: int = 0) -> ET.Element:
        """Make a CalDAV request and return parsed XML"""
        headers = {'Depth': str(depth)}
        response = self.session.request(method, url, data=body, headers=headers)
        
        if response.status_code == 401:
            raise Exception("Authentication failed - check APPLE_ID and APPLE_APP_PASSWORD")
        
        response.raise_for_status()
        
        if response.text:
            # Remove XML declaration if present
            text = re.sub(r'<\?xml[^?]*\?>', '', response.text)
            return ET.fromstring(text)
        return None
    
    def _href(self, elem: ET.Element) -> str:
        """Extract href text from element"""
        href = elem.find('.//{DAV:}href')
        return href.text if href is not None else ""
    
    def _displayname(self, elem: ET.Element) -> str:
        """Extract displayname text from element"""
        name = elem.find('.//{DAV:}displayname')
        return name.text if name is not None else ""
    
    def discover_principal(self) -> str:
        """Discover the user's principal URL"""
        if self._principal:
            return self._principal
        
        body = '''<?xml version="1.0"?>
<propfind xmlns="DAV:">
  <prop>
    <current-user-principal/>
  </prop>
</propfind>'''
        
        root = self._request('PROPFIND', self.base_url + '/', body, depth=0)
        
        # Find current-user-principal href
        for response in root.findall('.//{DAV:}response'):
            principal = response.find('.//{DAV:}current-user-principal/{DAV:}href')
            if principal is not None:
                self._principal = principal.text
                return self._principal
        
        raise Exception("Could not discover principal")
    
    def get_calendar_home(self) -> str:
        """Get the calendar home URL (handles shard URLs)"""
        if self._calendar_home:
            return self._calendar_home
        
        principal = self.discover_principal()
        
        # If principal is full URL, extract base
        if principal.startswith('https://'):
            parsed = urlparse(principal)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
            principal = parsed.path
        
        body = '''<?xml version="1.0"?>
<propfind xmlns="DAV:" xmlns:cal="urn:ietf:params:xml:ns:caldav">
  <prop>
    <cal:calendar-home-set/>
  </prop>
</propfind>'''
        
        root = self._request('PROPFIND', self.base_url + principal, body, depth=0)
        
        for response in root.findall('.//{DAV:}response'):
            home = response.find('.//{urn:ietf:params:xml:ns:caldav}calendar-home-set/{DAV:}href')
            if home is not None:
                href = home.text
                # If full URL, update base_url and return
                if href.startswith('https://'):
                    self._calendar_home = href
                    parsed = urlparse(href)
                    self.base_url = f"{parsed.scheme}://{parsed.netloc}"
                    return href
                else:
                    self._calendar_home = self.base_url + href
                    return self._calendar_home
        
        raise Exception("Could not find calendar home")
    
    def list_calendars(self) -> list:
        """List all available calendars"""
        calendar_home = self.get_calendar_home()
        
        body = '''<?xml version="1.0"?>
<propfind xmlns="DAV:" xmlns:cal="urn:ietf:params:xml:ns:caldav" xmlns:cs="http://calendarserver.org/ns/">
  <prop>
    <displayname/>
    <resourcetype/>
    <cal:supported-calendar-component-set/>
    <cs:read-only/>
  </prop>
</propfind>'''
        
        root = self._request('PROPFIND', calendar_home, body, depth=1)
        
        calendars = []
        for response in root.findall('.//{DAV:}response'):
            href = self._href(response)
            name = self._displayname(response)
            
            # Skip the root collection
            if href.rstrip('/').endswith('/calendars'):
                continue
            
            # Check if it's a calendar (has VEVENT support)
            resourcetype = response.find('.//{DAV:}resourcetype')
            is_calendar = resourcetype is not None and resourcetype.find('.//{urn:ietf:params:xml:ns:caldav}calendar') is not None
            
            if is_calendar and name:
                # Check read-only status
                readonly_elem = response.find('.//{http://calendarserver.org/ns/}read-only')
                readonly = readonly_elem is not None and readonly_elem.text == 'true'
                
                # Check if subscribed
                subscribed = resourcetype is not None and resourcetype.find('.//{http://calendarserver.org/ns/}subscribed') is not None
                
                calendars.append({
                    'name': name,
                    'href': href,
                    'url': self.base_url + href if not href.startswith('https') else href,
                    'readonly': readonly,
                    'subscribed': subscribed
                })
        
        return calendars
    
    def get_calendar_by_name(self, name: str) -> dict:
        """Get calendar by display name"""
        for cal in self.list_calendars():
            if cal['name'] == name:
                return cal
        return None
    
    def list_events(self, calendar_name: str = "Calendar", days: int = 7) -> list:
        """List events in date range"""
        calendar = self.get_calendar_by_name(calendar_name)
        if not calendar:
            raise Exception(f"Calendar '{calendar_name}' not found")
        
        # Calculate date range
        now = datetime.now()
        end = now + timedelta(days=days)
        
        # Get list of event files
        body = '''<?xml version="1.0"?>
<propfind xmlns="DAV:">
  <prop>
    <getcontenttype/>
    <getlastmodified/>
  </prop>
</propfind>'''
        
        root = self._request('PROPFIND', calendar['url'], body, depth=1)
        
        events = []
        for response in root.findall('.//{DAV:}response'):
            href = self._href(response)
            
            if not href.endswith('.ics'):
                continue
            
            # Fetch event
            event_url = self.base_url + href if not href.startswith('https') else href
            event_response = self.session.get(event_url)
            
            if event_response.status_code != 200:
                continue
            
            # Parse ICS
            event_data = self._parse_ics(event_response.text)
            if not event_data:
                continue
            
            # Check if in date range
            event_date = event_data.get('dtstart')
            if event_date and now <= event_date <= end:
                events.append(event_data)
        
        # Sort by date
        events.sort(key=lambda x: x.get('dtstart') or datetime.min)
        return events
    
    def _parse_ics(self, ics_text: str) -> dict:
        """Parse iCalendar data"""
        if Calendar:
            try:
                cal = Calendar.from_ical(ics_text)
                for component in cal.walk():
                    if component.name == "VEVENT":
                        return {
                            'summary': str(component.get('summary', 'Untitled')),
                            'dtstart': component.get('dtstart').dt if component.get('dtstart') else None,
                            'dtend': component.get('dtend').dt if component.get('dtend') else None,
                            'location': str(component.get('location', '')),
                            'description': str(component.get('description', '')),
                            'uid': str(component.get('uid', ''))
                        }
            except Exception:
                pass
        
        # Fallback: manual parsing
        result = {'summary': 'Untitled', 'dtstart': None, 'dtend': None, 
                  'location': '', 'description': '', 'uid': ''}
        
        for line in ics_text.split('\n'):
            line = line.strip()
            if line.startswith('SUMMARY:'):
                result['summary'] = line[8:]
            elif line.startswith('LOCATION:'):
                result['location'] = line[9:]
            elif line.startswith('DESCRIPTION:'):
                result['description'] = line[12:]
            elif line.startswith('UID:'):
                result['uid'] = line[4:]
            elif line.startswith('DTSTART'):
                # Extract date/time
                match = re.search(r':(\d{8})T?(\d{6})?', line)
                if match:
                    date_str = match.group(1)
                    time_str = match.group(2) or '000000'
                    result['dtstart'] = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
            elif line.startswith('DTEND'):
                match = re.search(r':(\d{8})T?(\d{6})?', line)
                if match:
                    date_str = match.group(1)
                    time_str = match.group(2) or '000000'
                    result['dtend'] = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
        
        return result
    
    def create_event(self, title: str, start: str, duration: int = 60,
                     all_day: bool = False, location: str = "", 
                     description: str = "", calendar_name: str = "Calendar") -> str:
        """Create a new event"""
        calendar = self.get_calendar_by_name(calendar_name)
        if not calendar:
            raise Exception(f"Calendar '{calendar_name}' not found")
        
        # Parse start time
        if all_day:
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=1)
        else:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00').replace('+00:00', ''))
            end_dt = start_dt + timedelta(minutes=duration)
        
        # Generate ICS
        if Calendar and Event:
            cal = Calendar()
            cal.add('prodid', '-//OpenClaw//iCloud CalDAV//EN')
            cal.add('version', '2.0')
            
            event = Event()
            event.add('uid', f"openclaw-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}@openclaw.local")
            event.add('dtstamp', datetime.now(timezone.utc))
            event.add('summary', title)
            event.add('description', description)
            if location:
                event.add('location', location)
            
            if all_day:
                event.add('dtstart', start_dt.date())
                event.add('dtend', end_dt.date())
            else:
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
            
            cal.add_component(event)
            ics_data = cal.to_ical().decode('utf-8')
        else:
            # Fallback: manual ICS generation
            uid = f"openclaw-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}@openclaw.local"
            dtstamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            
            lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//OpenClaw//iCloud CalDAV//EN",
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}"
            ]
            
            if all_day:
                lines.append(f"DTSTART;VALUE=DATE:{start_dt.strftime('%Y%m%d')}")
                lines.append(f"DTEND;VALUE=DATE:{end_dt.strftime('%Y%m%d')}")
            else:
                lines.append(f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M%S')}")
                lines.append(f"DTEND;TZID=Asia/Shanghai:{end_dt.strftime('%Y%m%dT%H%M%S')}")
            
            lines.append(f"SUMMARY:{title.encode('ascii', 'ignore').decode()}")
            if description:
                lines.append(f"DESCRIPTION:{description}")
            if location:
                lines.append(f"LOCATION:{location}")
            
            lines.extend(["END:VEVENT", "END:VCALENDAR"])
            ics_data = '\r\n'.join(lines)
        
        # Upload event
        filename = f"openclaw-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}.ics"
        event_url = calendar['url'].rstrip('/') + '/' + filename
        
        headers = {'Content-Type': 'text/calendar; charset=utf-8'}
        response = self.session.put(event_url, data=ics_data, headers=headers)
        
        if response.status_code not in (201, 204):
            raise Exception(f"Failed to create event: HTTP {response.status_code}")
        
        return event_url
    
    def delete_event(self, uid: str = None, filename: str = None, calendar_name: str = "Calendar") -> bool:
        """Delete an event by UID or filename"""
        calendar = self.get_calendar_by_name(calendar_name)
        if not calendar:
            raise Exception(f"Calendar '{calendar_name}' not found")
        
        event_url = None
        
        if filename:
            # Direct filename deletion
            event_url = calendar['url'].rstrip('/') + '/' + filename
        elif uid:
            # Search for event by UID
            body = '''<?xml version="1.0"?>
<propfind xmlns="DAV:">
  <prop>
    <getcontenttype/>
  </prop>
</propfind>'''
            
            root = self._request('PROPFIND', calendar['url'], body, depth=1)
            
            for response in root.findall('.//{DAV:}response'):
                href = self._href(response)
                if not href.endswith('.ics'):
                    continue
                
                # Fetch event and check UID
                event_url_full = self.base_url + href if not href.startswith('https') else href
                event_response = self.session.get(event_url_full)
                
                if event_response.status_code == 200 and uid in event_response.text:
                    event_url = event_url_full
                    break
        
        if not event_url:
            raise Exception("Event not found")
        
        # Delete the event
        response = self.session.delete(event_url)
        
        if response.status_code not in (200, 204):
            raise Exception(f"Failed to delete event: HTTP {response.status_code}")
        
        return True


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='iCloud CalDAV CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # list-calendars command
    subparsers.add_parser('list-calendars', help='List all calendars')
    
    # list-events command
    list_parser = subparsers.add_parser('list-events', help='List events')
    list_parser.add_argument('--days', type=int, default=7, help='Number of days to look ahead')
    list_parser.add_argument('--calendar', default='Calendar', help='Calendar name')
    
    # create-event command
    create_parser = subparsers.add_parser('create-event', help='Create a new event')
    create_parser.add_argument('--title', required=True, help='Event title')
    create_parser.add_argument('--start', required=True, help='Start time (ISO8601 or YYYY-MM-DD)')
    create_parser.add_argument('--duration', type=int, default=60, help='Duration in minutes')
    create_parser.add_argument('--all-day', action='store_true', help='Create all-day event')
    create_parser.add_argument('--location', default='', help='Location')
    create_parser.add_argument('--description', default='', help='Description')
    create_parser.add_argument('--calendar', default='Calendar', help='Target calendar')
    
    # delete-event command
    delete_parser = subparsers.add_parser('delete-event', help='Delete an event')
    delete_parser.add_argument('--uid', help='Event UID to delete')
    delete_parser.add_argument('--file', help='Event filename to delete (e.g., event.ics)')
    delete_parser.add_argument('--calendar', default='Calendar', help='Calendar name')
    
    args = parser.parse_args()
    
    # Check credentials
    apple_id = os.environ.get('APPLE_ID')
    app_password = os.environ.get('APPLE_APP_PASSWORD')
    
    if not apple_id or not app_password:
        print("Error: APPLE_ID and APPLE_APP_PASSWORD environment variables required")
        print("Generate app-specific password at: https://appleid.apple.com")
        sys.exit(1)
    
    # Initialize client
    try:
        client = iCloudCalDAV(apple_id, app_password)
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'list-calendars':
            print("Fetching calendars...\n")
            calendars = client.list_calendars()
            print("Available Calendars:\n")
            for cal in calendars:
                status = []
                if cal['readonly']:
                    status.append('read-only')
                if cal['subscribed']:
                    status.append('subscribed')
                status_str = f" ({', '.join(status)})" if status else ""
                print(f"  • {cal['name']}{status_str}")
                print(f"    Path: {cal['href']}\n")
        
        elif args.command == 'list-events':
            print(f"Fetching events for next {args.days} days from '{args.calendar}'...\n")
            events = client.list_events(args.calendar, args.days)
            if not events:
                print(f"No events found in the next {args.days} days.")
            else:
                for event in events:
                    print(f"📅 {event['summary']}")
                    dt = event.get('dtstart')
                    if dt:
                        if isinstance(dt, datetime):
                            print(f"   When: {dt.strftime('%Y-%m-%d at %H:%M')}")
                        else:
                            print(f"   When: {dt} (all-day)")
                    if event.get('location'):
                        print(f"   Where: {event['location']}")
                    print()
        
        elif args.command == 'create-event':
            print("Creating event...")
            event_url = client.create_event(
                title=args.title,
                start=args.start,
                duration=args.duration,
                all_day=args.all_day,
                location=args.location,
                description=args.description,
                calendar_name=args.calendar
            )
            print(f"✅ Event created successfully!")
            print(f"   Title: {args.title}")
            if args.all_day:
                print(f"   When: {args.start} (all-day)")
            else:
                print(f"   When: {args.start} ({args.duration} min)")
            if args.location:
                print(f"   Where: {args.location}")
            print(f"   Calendar: {args.calendar}")
        
        elif args.command == 'delete-event':
            if not args.uid and not args.file:
                print("Error: Either --uid or --file is required")
                sys.exit(1)
            
            print(f"Deleting event from '{args.calendar}'...")
            client.delete_event(
                uid=args.uid,
                filename=args.file,
                calendar_name=args.calendar
            )
            print("✅ Event deleted successfully!")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()