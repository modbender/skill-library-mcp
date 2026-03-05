#!/usr/bin/env python3
"""YouTube Shorts 업로드 스크립트

사용법:
  python3 youtube_upload.py --file VIDEO.mp4 --title "제목" --description "설명" [--tags "tag1,tag2"]

첫 실행 시 OAuth 브라우저 인증이 필요합니다.
인증 토큰은 token.json에 저장되어 재사용됩니다.
"""

import argparse
import os
import sys
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SCRIPT_DIR = Path(__file__).parent
CLIENT_SECRET_FILE = SCRIPT_DIR / "client_secret.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"


def get_authenticated_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                print(f"ERROR: {CLIENT_SECRET_FILE} not found!")
                print("Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고")
                print(f"JSON 파일을 {CLIENT_SECRET_FILE}에 저장하세요.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=8090, open_browser=True)

        TOKEN_FILE.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, file_path, title, description, tags=None, category="22"):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(file_path, chunksize=1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"업로드 중: {file_path}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  진행: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ 업로드 완료! https://youtube.com/shorts/{video_id}")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts 업로드")
    parser.add_argument("--file", required=True, help="영상 파일 경로")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--description", default="", help="영상 설명")
    parser.add_argument("--tags", default="", help="태그 (쉼표 구분)")
    parser.add_argument("--privacy", default="public", choices=["public", "private", "unlisted"])
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: 파일을 찾을 수 없습니다: {args.file}")
        sys.exit(1)

    youtube = get_authenticated_service()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    video_id = upload_video(youtube, args.file, args.title, args.description, tags)
    return video_id


if __name__ == "__main__":
    main()
