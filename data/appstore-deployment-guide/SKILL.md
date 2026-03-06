---
name: appstore-deployment-guide
description: "Complete guide to deploying iOS apps to the Apple App Store. Covers Apple Developer accounts (individual and organization), certificates, provisioning, App Store Connect, TestFlight, build submission, app review, subscriptions, privacy compliance, and common rejection fixes. Supports both native Xcode and React Native/Expo (EAS) workflows."
---

# App Store Deployment Guide

A complete, practical guide to getting your iOS app published — from zero to live on the App Store. Based on real deployment experience, not just documentation.

## What This Skill Covers

1. **Apple Developer Account Setup** — Individual vs Organization, D-U-N-S numbers, business entity requirements
2. **Certificates & Code Signing** — Development, distribution, provisioning profiles, push notifications
3. **App Store Connect** — App listing, metadata, screenshots, privacy nutrition labels
4. **Building & Submitting** — Both Xcode (native) and Expo/EAS (React Native) paths
5. **TestFlight** — Internal and external beta testing
6. **App Review** — Common rejections and exactly how to fix them
7. **Subscriptions & Revenue** — Apple's commission, RevenueCat, Small Business Program
8. **Privacy & Compliance** — ATT, nutrition labels, export compliance
9. **Post-Launch** — Crash monitoring, ASO, phased releases

## Key Gotchas (Preview)

These are the issues that cost real developers days of wasted time:

- ⚠️ **Build number must increment every submission** — or Apple silently rejects your upload. Hours wasted on free-tier build queues.
- ⚠️ **Account deletion is REQUIRED** — Apple mandates users can delete their account from within the app
- ⚠️ **Password recovery is REQUIRED** — No reset flow = guaranteed rejection
- ⚠️ **Organization accounts need a D-U-N-S number** — free but takes up to 30 days
- ⚠️ **Privacy nutrition labels** — you must declare every data type your app touches
- ⚠️ **Demo account required** — if your app has login, reviewers need test credentials

> *The premium version explains each of these in detail with step-by-step solutions.*

## Sample Workflow

*"I have a React Native/Expo app ready to deploy. What do I need?"*

The premium skill walks through:
1. Apple Developer enrollment ($99/year) — which account type and why
2. Certificate and provisioning profile setup
3. app.json / app.config.js configuration for EAS
4. `eas build --platform ios` with proper build profiles
5. TestFlight upload and beta testing strategy
6. App Store Connect metadata (with exact screenshot dimensions)
7. Submission and review preparation
8. Common rejection fixes with specific solutions

## Get the Full Version

This free edition provides an overview. The **Premium Edition** ($10) includes:

✅ Step-by-step Apple Developer account setup (individual AND organization)
✅ All 50 states + DC — business formation docs, filing fees, where to file, processing times
✅ Complete certificate & provisioning guide with troubleshooting
✅ App Store Connect setup with exact screenshot dimensions per device
✅ Build & submit for BOTH Xcode and Expo/EAS (with version numbering gotchas)
✅ TestFlight testing guide (internal + external)
✅ Every common App Review rejection with specific fixes
✅ Subscription setup with RevenueCat + Apple Small Business Program
✅ Privacy compliance checklist (ATT, nutrition labels, GDPR/CCPA)
✅ Google Play comparison for cross-platform developers
✅ Cost-saving tips (Google AI Studio $300 free credits for AI-powered apps)

**👉 https://kulickster0.gumroad.com/l/mwfpmt**

Built from real deployment experience. Save yourself weeks of trial and error.
