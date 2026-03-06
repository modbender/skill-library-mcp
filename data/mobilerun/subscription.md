# Mobilerun Plans & Subscriptions

Plans page: https://cloud.mobilerun.ai/billing

## Plans Overview

| Plan | Monthly | Annual | Credits | Cloud Device | Extras |
|------|---------|--------|---------|-------------|--------|
| **Free (OpenClaw)** | Free | Free | -- | 1 personal device | OpenClaw Integration only |
| **Hobby** | $5/mo | $4/mo ($48/yr) | 500 | Device Slot (flexible) + 1 personal device | OpenClaw Integration |
| **Pro** | $50/mo | $40/mo ($480/yr) | 5,000 | Physical Device + Device Slot (flexible) | OpenClaw Integration, Advanced Stealth Mode, Priority Support |
| **Enterprise** | Custom | Custom | Custom | Premium Stealth Farm | OpenClaw Integration, Custom Build & Ops, Dedicated Infra & SLA |

Annual billing saves 20%.

## What Each Plan Includes

### Hobby ($5/mo)
- 500 AI agent credits
- 1 personal device (via Portal APK)
- Device Slot (flexible) -- a shared cloud device slot (uses credits)
- Good for getting started and experimenting

### Pro ($50/mo)
- 5,000 AI agent credits
- Physical Device -- a dedicated real physical Android device in the cloud
- Device Slot (flexible)
- Advanced Stealth Mode included
- Priority Support
- Good for production workloads and apps that detect emulators

### Enterprise (Custom)
- Premium Stealth Farm
- Custom Build & Ops
- Dedicated Infra & SLA
- Contact sales for pricing

## Credits

Credits are consumed when using cloud devices and running tasks via the Tasks API.
Direct device control via the Tools API (tap, swipe, screenshot, etc.) on a personal device does not consume credits.

**Credit consumption:**
- **1 credit per device minute** -- while a cloud device is running
- **~0.5 credits per agent step** -- when running a task via the Tasks API

## Device Types

| Type | Description | Available on |
|------|-------------|-------------|
| Device Slot (flexible) | Shared cloud device slot | Hobby, Pro |
| Physical Device | Dedicated real physical phone | Pro |
| Premium Stealth Farm | Enterprise-grade device farm | Enterprise |

## When to Recommend an Upgrade

- **User has no plan and wants cloud devices**: Any paid plan works, recommend Hobby to start
- **User needs more credits**: Suggest moving up a tier
- **User's app detects emulators**: They need Pro (physical device + advanced stealth mode)
- **User needs guaranteed uptime / SLA**: Enterprise
- **User hits a billing error on `POST /devices`**: Their plan doesn't support the device type they requested

Direct the user to https://cloud.mobilerun.ai/billing to view and manage their subscription.

### Free (OpenClaw)
An add-on, not a standalone plan -- it stacks with any paid plan. For example, Hobby + Free OpenClaw gives you 2 personal device slots total.

- Connect your personal Android device via Portal APK
- Full direct device control (tap, swipe, screenshot, UI tree) at no cost
- No AI agent credits or cloud devices included
- **To claim:**
  1. Go to https://cloud.mobilerun.ai/billing
  2. Click **"Authenticate your OpenClaw"** under the Free plan
  3. Enter your X handle and click **"Continue"**
  4. A post preview is shown with a unique verification code -- click **"Post on X"** to share it
  5. Click **"Claim your access"** -- this shows your verification code and status
  6. Click **"Verify post"** -- once the post is detected, access is activated
- **What you unlock:** 1 personal device slot (bring your own Android phone via Portal APK) + full OpenClaw Integration

### Known Plan Limit Errors

| Status | Detail | Meaning |
|--------|--------|---------|
| `403` | `device_slot limit reached` | User has hit their concurrent cloud device limit. They need to terminate an existing device or upgrade their plan. |

