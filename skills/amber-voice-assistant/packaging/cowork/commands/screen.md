---
name: screen
description: Start or stop inbound call screening on your Twilio number
arguments:
  - name: action
    description: "start" to begin screening, "stop" to disable, "status" to check
    required: true
---

# /amber:screen

Control inbound call screening. When active, Amber answers incoming calls, identifies the caller, takes a message, and delivers a summary.

## Usage

```
/amber:screen start
/amber:screen stop
/amber:screen status
```

## Screening flow

1. Amber answers the incoming call with a friendly greeting
2. Asks who's calling and what it's regarding
3. Collects: caller name, callback number, message
4. Delivers a summary to you with all captured details
5. Optionally checks your calendar for availability if the caller wants to book time

## Customization

Edit the personality and greeting in AGENT.md to change how Amber handles calls.
