---
name: Meta Ads Analytics & Event Finder
description: A powerful toolkit to monitor your Meta (Facebook/Instagram)
  advertising performance directly through chat. This bundle includes analytics
  reporting and an event discovery tool to ensure accurate t...
---

# Meta Ads Analytics & Event Finder

A powerful toolkit to monitor your Meta (Facebook/Instagram) advertising performance directly through chat. This bundle includes analytics reporting and an event discovery tool to ensure accurate tracking.

## 🚀 Capabilities

1.  **Ad Performance Reporting:**
    * Calculates **Spend**, **Conversions**, and **CAC (Cost Per Acquisition)**.
    * Breaks down data by **Ad Set**.
    * Supports natural language date ranges (e.g., "yesterday", "last month", "last 7 days").

2.  **Event Discovery Tool:**
    * Lists all raw event names (e.g., `offsite_conversion.custom...`) currently active in your ad account.
    * Helps you find the exact event name to configure for conversion tracking.

---

## ⚙️ Configuration (.env)

To use this skill, you must set the following environment variables in your OpenClaw setup:

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `META_ACCESS_TOKEN` | User Access Token from Meta Developers | **Yes** | - |
| `META_AD_ACCOUNT_ID` | Ad Account ID (must start with `act_`) | **Yes** | - |
| `META_EVENT_NAME` | The specific conversion event to track | No | `offsite_conversion.fb_pixel_custom` |

---

## 🔑 How to Get Credentials

### 1. Get Access Token
1.  Go to [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2.  Select your App.
3.  Add Permissions: `ads_read`, `read_insights`.
4.  Click **Generate Access Token** and copy the string.

### 2. Get Ad Account ID
1.  Go to [Facebook Ads Manager](https://adsmanager.facebook.com/).
2.  Check the URL for `act=12345678`.
3.  Your ID is `act_12345678` (Don't forget the `act_` prefix).

---

## 💬 Example Commands

### check Analytics
> "Show me yesterday's ad performance"
> "Calculate CAC for the last 7 days"
> "How were the ads from 2026-02-01 to 2026-02-10?"
> "Report ad spend for this month"

### Find Correct Event Name
> "List all ad events"
> "Show me available meta events"

---

## ⚠️ Troubleshooting

**Q: My conversion count is 0, but I have sales.**
**A:** The default event is `offsite_conversion.fb_pixel_custom`. Your pixel might be using a different name like `purchase`, `lead`, or `start_trial`.
1.  Ask the bot: **"List all ad events"**.
2.  Copy the exact raw name from the list.
3.  Update your `META_EVENT_NAME` variable with that name.
