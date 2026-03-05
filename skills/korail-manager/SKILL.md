---
name: korail-manager
version: 1.1.4
description: "Korail(KTX) & SRT reservation automation skill. Search, reserve, and watch for tickets. Supports Telegram and Slack notifications. (English/Korean supported)"
tools:
  # ── KTX ──
  - name: korail_search
    description: "Search for KTX trains between two stations."
    parameters:
      type: object
      properties:
        dep: { type: string, description: "Departure station (e.g. 서울, 대전)" }
        arr: { type: string, description: "Arrival station (e.g. 부산, 동대구)" }
        date: { type: string, description: "YYYYMMDD format (default: today)" }
        time: { type: string, description: "HHMMSS format (default: now)" }
      required: [dep, arr]
    command: ["python3", "scripts/search.py"]

  - name: korail_watch
    description: "Watch for available KTX seats and reserve automatically. Sends Telegram/Slack alert on success."
    parameters:
      type: object
      properties:
        dep: { type: string, description: "Departure station" }
        arr: { type: string, description: "Arrival station" }
        date: { type: string, description: "YYYYMMDD" }
        start_time: { type: number, description: "Start hour (0-23)" }
        end_time: { type: number, description: "End hour (0-23)" }
        interval: { type: number, description: "Check interval in seconds (default: 300)" }
      required: [dep, arr, date, start_time, end_time]
    command: ["python3", "scripts/watch.py"]

  - name: korail_cancel
    description: "Cancel KTX reservations. If --date is specified, only cancels reservations on that date."
    parameters:
      type: object
      properties:
        date: { type: string, description: "Target date to cancel (YYYYMMDD). If omitted, cancels all." }
    command: ["python3", "scripts/cancel.py"]

  # ── SRT ──
  - name: srt_search
    description: "Search for SRT trains between two stations."
    parameters:
      type: object
      properties:
        dep: { type: string, description: "Departure station (e.g. 수서, 오송, 대전)" }
        arr: { type: string, description: "Arrival station (e.g. 부산, 대전, 동대구)" }
        date: { type: string, description: "YYYYMMDD format (default: today)" }
        time: { type: string, description: "HHMMSS format (default: now)" }
      required: [dep, arr]
    command: ["python3", "scripts/srt_search.py"]

  - name: srt_watch
    description: "Watch for available SRT seats and reserve automatically. Sends Telegram/Slack alert on success."
    parameters:
      type: object
      properties:
        dep: { type: string, description: "Departure station" }
        arr: { type: string, description: "Arrival station" }
        date: { type: string, description: "YYYYMMDD" }
        start_time: { type: number, description: "Start hour (0-23)" }
        end_time: { type: number, description: "End hour (0-23)" }
        interval: { type: number, description: "Check interval in seconds (default: 300)" }
      required: [dep, arr, date, start_time, end_time]
    command: ["python3", "scripts/srt_watch.py"]

  - name: srt_cancel
    description: "Cancel SRT reservations. If --date is specified, only cancels reservations on that date."
    parameters:
      type: object
      properties:
        date: { type: string, description: "Target date to cancel (YYYYMMDD). If omitted, cancels all." }
    command: ["python3", "scripts/cancel_srt.py"]

dependencies:
  python:
    - requests
    - pycryptodome
    - python-dotenv
    - six

browserActions:
  - label: "KTX 좌석 검색"
    prompt: korail_search --dep "서울" --arr "부산"
  - label: "KTX 잔여석 감시 및 예약"
    prompt: korail_watch --dep "부산" --arr "서울" --date "20260210" --start-time 9 --end-time 18
  - label: "KTX 예약 취소"
    prompt: korail_cancel
  - label: "SRT 좌석 검색"
    prompt: srt_search --dep "수서" --arr "대전"
  - label: "SRT 잔여석 감시 및 예약"
    prompt: srt_watch --dep "수서" --arr "대전" --date "20260210" --start-time 9 --end-time 18
  - label: "SRT 예약 취소"
    prompt: srt_cancel
