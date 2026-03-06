# Setup Guide

## Step 1 – Create Google Sheet

Create sheet with columns:

Date | Product Name | Product URL | Product Type | Classification | Priority | Task Title | Summary | Affected Area | Severity | Customer Risk | Update Required | Status | Comment Text | Comment URL

## Step 2 – Create Google Apps Script Webhook

Use Apps Script to accept POST requests and append rows.

## Step 3 – Connect Skill Output to Webhook

Send skill JSON output via POST request to Apps Script endpoint.

---

This enables:

Envato Comment → AI Task → Google Sheet → Task Tracking