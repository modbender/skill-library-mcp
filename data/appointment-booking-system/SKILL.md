---
name: appointment-booking-system
description: Generic appointment booking and management system for service businesses. Booking intake, confirmation, automated reminders (24h, 2h), no-show followup, and daily schedule reports. 5 production-ready n8n workflows with Google Sheets backend.
tags: [booking, appointments, scheduling, reminders, no-show, automation, n8n, google-sheets]
author: mhmalvi
version: 1.2.0
license: CC BY-NC-SA 4.0
metadata:
  clawdbot:
    emoji: "\U0001F4C5"
    requires:
      n8nCredentials: [google-sheets-oauth2, smtp]
      env: [BUSINESS_NAME, BUSINESS_PHONE, STAFF_EMAIL]
    os: [linux, darwin, win32]
---

# Appointment Booking System

A complete appointment booking and management system for service businesses. Handles booking intake, confirmation emails, automated reminders, no-show detection, and daily schedule reports.

## Problem

Service businesses (salons, clinics, consultants, studios) lose revenue from missed appointments, no-shows, and scheduling chaos. Booking platforms charge $30-100+/month and often lack customization. Manual reminders are unreliable.

This system provides self-hosted booking management with zero monthly fees.

## What It Does

1. **Booking Intake** — Webhook API receives bookings, validates fields, generates booking ID, stores in Sheets
2. **Confirmation** — Sends confirmation email to client and notification to staff immediately
3. **Smart Reminders** — Sends 24-hour and 2-hour reminders automatically
4. **No-Show Followup** — Detects missed appointments and sends rescheduling email
5. **Daily Schedule** — Morning email with today's and tomorrow's appointments plus weekly stats

## Included Workflows

| # | File | Purpose |
|---|------|---------|
| 01 | `01-booking-intake.json` | Webhook → validate → store → confirm client → notify staff |
| 02 | `02-booking-confirmation.json` | Update booking status (confirm/cancel) via webhook |
| 03 | `03-reminder-engine.json` | Hourly check → send 24h and 2h reminders |
| 04 | `04-noshow-followup.json` | Check past appointments → detect no-shows → followup email |
| 05 | `05-daily-schedule.json` | Morning report with today's schedule and weekly stats |

## Architecture

```
Client books online (form/API)
    |
    v
Workflow 01: Booking Intake
    +-> Validate required fields
    +-> Generate booking ID
    +-> Save to Google Sheets
    +-> Email confirmation to client
    +-> Email notification to staff
    +-> Return booking ID

Status update (confirm/cancel):
    |
    v
Workflow 02: Booking Confirmation
    +-> Update status in Sheets

Hourly:
    |
    v
Workflow 03: Reminder Engine
    +-> Read confirmed appointments
    +-> Check: is appointment in 24h? -> send reminder
    +-> Check: is appointment in 2h? -> send reminder
    +-> Mark reminders as sent in Sheets

Every 2 hours:
    |
    v
Workflow 04: No-Show Followup
    +-> Check past appointments (1-48h ago)
    +-> IF no showed_up status -> mark as no-show
    +-> Send rescheduling email

Daily at 7 AM:
    |
    v
Workflow 05: Daily Schedule
    +-> Build today's and tomorrow's schedule tables
    +-> Calculate weekly stats (completed, no-shows, cancelled)
    +-> Email to staff
```

## Required n8n Credentials

| Credential Type | Used For | Placeholder in JSON |
|----------------|----------|---------------------|
| Google Sheets OAuth2 | Appointment storage | `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` |
| SMTP | Confirmations, reminders, reports | `YOUR_SMTP_CREDENTIAL_ID` |

## Environment Variables

```bash
# Business Details (used in client-facing emails)
BUSINESS_NAME=Your Business Name
BUSINESS_PHONE=+1234567890
STAFF_EMAIL=staff@yourbusiness.com
```

> **Note:** The Google Sheet ID is configured as a `YOUR_BOOKING_SHEET_ID` placeholder in the workflow JSON files (not an environment variable). Replace it directly in n8n after import.

## Configuration Placeholders

| Placeholder | Description |
|-------------|-------------|
| `YOUR_BOOKING_SHEET_ID` | Google Sheet ID for appointments |
| `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` | n8n Google Sheets credential ID |
| `YOUR_SMTP_CREDENTIAL_ID` | n8n SMTP credential ID |
| `YOUR_NOTIFICATION_EMAIL` | Staff email for schedule reports |

## Google Sheets Schema (Appointments)

| Column | Type | Description |
|--------|------|-------------|
| booking_id | text | Unique booking ID (auto-generated) |
| name | text | Client full name |
| email | text | Client email |
| phone | text | Client phone |
| service | text | Service type (e.g., haircut, consultation) |
| date | date | Appointment date (YYYY-MM-DD) |
| time | text | Appointment time (HH:MM) |
| notes | text | Client notes |
| status | text | confirmed / cancelled / no-show / completed |
| showed_up | boolean | Whether client attended |
| reminder_24h | boolean | 24h reminder sent |
| reminder_2h | boolean | 2h reminder sent |
| created_at | datetime | Booking creation timestamp |

## Quick Start

### 1. Prerequisites
- n8n v2.4+ (self-hosted)
- Google Sheets OAuth2 credentials
- SMTP email credentials

### 2. Create Appointments Sheet
Create a Google Sheet with the columns above. Name the tab "Appointments".

### 3. Import & Configure
Import all 5 JSON files into n8n. Replace all `YOUR_*` placeholders and set environment variables.

### 4. Test Booking
```bash
curl -X POST https://your-n8n.com/webhook/booking/new \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1234567890",
    "service": "Consultation",
    "date": "2026-03-10",
    "time": "14:00",
    "notes": "First visit"
  }'
```

## Use Cases

1. **Hair salons** — Booking, reminders, and no-show tracking for stylists
2. **Medical/dental clinics** — Patient appointment management
3. **Consultants** — Strategy call scheduling with automated reminders
4. **Fitness studios** — Class and personal training bookings
5. **Auto repair shops** — Service appointment scheduling

## Requirements

- n8n v2.4+ (self-hosted or cloud)
- Google Sheets OAuth2 credentials
- SMTP email credentials
