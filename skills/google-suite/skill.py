"""
Google Suite Skill
Provides unified access to Gmail, Google Calendar, and Google Drive APIs.
"""
import os
import pickle
from typing import Any, Dict
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for Gmail, Calendar, and Drive
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
]

TOKEN_PATH = Path(__file__).parent / 'google_suite_tokens.json'
CREDENTIALS_PATH = Path(__file__).parent / 'google_suite_credentials.json'


def get_skill_info():
    return {
        "slug": "google-suite",
        "display_name": "Google Suite Skill",
        "tags": ["google", "gmail", "calendar", "drive", "api", "automation"],
        "description": "Unified access to Gmail, Google Calendar, and Google Drive APIs."
    }


def get_credentials() -> Credentials:
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
                        "client_secret": os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
                        "redirect_uris": [os.environ.get("GOOGLE_OAUTH_REDIRECT_URI")],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


class GoogleSuiteSkill:
    def __init__(self):
        self.creds = get_credentials()

    def execute(self, params: Dict[str, Any]) -> Any:
        service = params.get("service")
        action = params.get("action")
        if service == "gmail":
            return self._handle_gmail(action, params)
        elif service == "calendar":
            return self._handle_calendar(action, params)
        elif service == "drive":
            return self._handle_drive(action, params)
        else:
            raise ValueError("Unknown service: {}".format(service))

    # Gmail operations
    def _handle_gmail(self, action, params):
        gmail = build('gmail', 'v1', credentials=self.creds)
        if action == "send":
            return self._gmail_send(gmail, params)
        elif action == "list":
            return self._gmail_list(gmail, params)
        elif action == "delete":
            return self._gmail_delete(gmail, params)
        else:
            raise ValueError(f"Unknown Gmail action: {action}")

    def _gmail_send(self, gmail, params):
        from email.mime.text import MIMEText
        import base64
        message = MIMEText(params.get("body", ""))
        message['to'] = params.get("to")
        message['subject'] = params.get("subject", "")
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        sent = gmail.users().messages().send(userId="me", body=body).execute()
        return {"id": sent.get("id"), "status": "sent"}

    def _gmail_list(self, gmail, params):
        query = params.get("query", "in:inbox")
        max_results = int(params.get("max_results", 10))
        results = gmail.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            msg_detail = gmail.users().messages().get(userId="me", id=msg['id']).execute()
            snippet = msg_detail.get('snippet', '')
            emails.append({"id": msg['id'], "snippet": snippet})
        return emails

    def _gmail_delete(self, gmail, params):
        msg_id = params.get("message_id")
        if not msg_id:
            raise ValueError("message_id is required for delete action")
        gmail.users().messages().delete(userId="me", id=msg_id).execute()
        return {"id": msg_id, "status": "deleted"}

    # Calendar operations
    def _handle_calendar(self, action, params):
        calendar = build('calendar', 'v3', credentials=self.creds)
        if action == "list":
            return self._calendar_list(calendar, params)
        elif action == "create":
            return self._calendar_create(calendar, params)
        elif action == "update":
            return self._calendar_update(calendar, params)
        elif action == "delete":
            return self._calendar_delete(calendar, params)
        else:
            raise ValueError(f"Unknown Calendar action: {action}")

    def _calendar_list(self, calendar, params):
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat() + 'Z'
        days = int(params.get("days", 7))
        end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
        events_result = calendar.events().list(
            calendarId='primary', timeMin=now, timeMax=end,
            maxResults=int(params.get("max_events", 10)), singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return [{"id": e["id"], "summary": e.get("summary"), "start": e["start"], "end": e["end"]} for e in events]

    def _calendar_create(self, calendar, params):
        event = {
            'summary': params.get('summary'),
            'start': {'dateTime': params.get('start')},
            'end': {'dateTime': params.get('end')},
        }
        created = calendar.events().insert(calendarId='primary', body=event).execute()
        return {"id": created["id"], "status": "created"}

    def _calendar_update(self, calendar, params):
        event_id = params.get('event_id')
        if not event_id:
            raise ValueError("event_id is required for update action")
        event = calendar.events().get(calendarId='primary', eventId=event_id).execute()
        if 'summary' in params:
            event['summary'] = params['summary']
        if 'start' in params:
            event['start']['dateTime'] = params['start']
        if 'end' in params:
            event['end']['dateTime'] = params['end']
        updated = calendar.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return {"id": updated["id"], "status": "updated"}

    def _calendar_delete(self, calendar, params):
        event_id = params.get('event_id')
        if not event_id:
            raise ValueError("event_id is required for delete action")
        calendar.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"id": event_id, "status": "deleted"}

    # Drive operations
    def _handle_drive(self, action, params):
        drive = build('drive', 'v3', credentials=self.creds)
        if action == "list":
            return self._drive_list(drive, params)
        elif action == "upload":
            return self._drive_upload(drive, params)
        elif action == "download":
            return self._drive_download(drive, params)
        elif action == "delete":
            return self._drive_delete(drive, params)
        else:
            raise ValueError(f"Unknown Drive action: {action}")

    def _drive_list(self, drive, params):
        query = params.get("query", "")
        max_files = int(params.get("max_files", 10))
        results = drive.files().list(q=query, pageSize=max_files, fields="files(id, name)").execute()
        files = results.get('files', [])
        return [{"id": f["id"], "name": f["name"]} for f in files]

    def _drive_upload(self, drive, params):
        from googleapiclient.http import MediaFileUpload
        file_path = params.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise ValueError("file_path is required and must exist for upload action")
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return {"id": uploaded["id"], "status": "uploaded"}

    def _drive_download(self, drive, params):
        file_id = params.get("file_id")
        dest_path = params.get("dest_path")
        if not file_id or not dest_path:
            raise ValueError("file_id and dest_path are required for download action")
        request = drive.files().get_media(fileId=file_id)
        with open(dest_path, 'wb') as f:
            from googleapiclient.http import MediaIoBaseDownload
            import io
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return {"id": file_id, "status": "downloaded", "path": dest_path}

    def _drive_delete(self, drive, params):
        file_id = params.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for delete action")
        drive.files().delete(fileId=file_id).execute()
        return {"id": file_id, "status": "deleted"}
