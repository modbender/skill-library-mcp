import argparse
import os
import sys
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service(client_secret_file):
    creds = None
    token_file = 'token.pickle'
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_file):
                print(f"Error: Client secret file not found at {client_secret_file}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file, title, description, privacy_status):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': '22' # People & Blogs
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    # Resumable upload for large files
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )

    print(f"Starting upload for {file}...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print("\nUpload Complete!")
    video_id = response.get('id')
    print(f"Video ID: {video_id}")
    print(f"Link: https://youtu.be/{video_id}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload a video to YouTube.')
    parser.add_argument('--file', required=True, help='Path to the video file.')
    parser.add_argument('--title', required=True, help='Title of the video.')
    parser.add_argument('--description', default='', help='Description of the video.')
    parser.add_argument('--privacy', default='unlisted', choices=['public', 'private', 'unlisted'], help='Privacy status.')
    parser.add_argument('--secrets', default='client_secret.json', help='Path to the client_secret.json file.')
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: Video file not found at {args.file}")
        sys.exit(1)

    youtube_service = get_authenticated_service(args.secrets)
    upload_video(youtube_service, args.file, args.title, args.description, args.privacy)
