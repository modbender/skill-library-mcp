---
name: kmong
description: kmong
---


# Kmong Automation Skill 🐧

## Registration Process (OpenClaw Browser)

### 1. Sign Up
```
1. browser open → https://kmong.com
2. Click sign up (ref: sign up link)
3. Select Google login (Google logo button)
4. Select Google account → Click "Continue"
5. Select "Act as Expert"
6. Check agree all → "Sign up complete"
```

### 2. Identity Verification (PASS SMS)
```
1. Click "Mobile phone verification" → Popup tab opens
2. Check popup tab targetId (query tabs)
3. Select carrier radio: click via evaluate
   - document.querySelectorAll('input[type=radio]')[0].click()  // SKT
   - [1] = KT, [2] = LGU+
4. Agree all: document.querySelectorAll('input[type=checkbox]')[0].click()
5. Click "Verify with SMS"
6. Enter name, birthdate(6 digits), 7th digit of SSN, phone number, security characters
7. Read security characters via screenshot
8. "Confirm" → Enter SMS verification code → "Confirm"
9. In main tab, agree to seller terms → "Expert registration complete"
```

### 3. Cautions
- When checkbox ref doesn't work: Use `evaluate` with `document.querySelectorAll('input[type=checkbox]')[0].click()`
- Cannot use `const`/`let` — Use `var` or no declaration
- Cannot chain multiple statements with semicolon — One statement per evaluate
- PASS verification popup is separate tab — Need to check targetId via tabs query
- Security characters (captcha): Take screenshot and read as image

### 4. Profile Setup
```
1. Change nickname: "Edit" button → Select all text (Meta+a) → Enter new nickname → "Save"
2. Expertise: Click "Select service fields"
3. Introduction: Click "Write introduction"
4. Register service: Click "Register service"
```

### 5. Service Registration Tips
- Title: Include SEO keywords (e.g., "AI Chatbot Development | Student Council Organization Management Automation")
- Price: 3 tiers (Standard/Deluxe/Premium)
- Description: 500+ chars, specify concrete deliverables
- Category: IT·Programming > Chatbot Development / Task Automation

## Account Information
- Email: Configure in `~/.secrets/kmong.env`
- Nickname: Configure in workspace settings
- Profile: https://kmong.com/@[your-username]

---
> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
