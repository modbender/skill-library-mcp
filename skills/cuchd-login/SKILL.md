---
name: cuchd-login
description: something
version: 1.0.0
---

# CUCHD Staff Portal Login

Login URL: `https://staff.cuchd.in`

The login form is a **two-step process**. The password field is hidden until after the username is submitted and the page reloads.

---

## Step-by-Step Login Flow

### Step 1 — Navigate to the portal

```
browser: navigate to https://staff.cuchd.in
```

Wait for the page to fully load.

---

### Step 2 — Enter Username / User ID

- Locate the username or user ID input field (usually labelled "Username", "User ID", or "Employee ID")
- Type the username into the field

```
browser: type "<username>" into the username field
```

- Click the **Next** button (may be labelled "Next", "Continue", or similar)

```
browser: click the Next / Continue button
```

---

### Step 3 — Wait for page reload

The page will reload or update dynamically. The password field is **not visible before this step** — wait until the new state is fully loaded before proceeding.

```
browser: wait for the password field to appear
```

---

### Step 4 — Enter Password

- Locate the now-visible password input field
- Type the password into it

```
browser: type "<password>" into the password field
```

---

### Step 5 — Click Login

- Click the **Login** button (now visible after page reload)

```
browser: click the Login button
```

---

### Step 6 — Confirm Login

- Wait for the dashboard or home page to load
- Confirm successful login by checking the page title or welcome message
- Report back to the user: logged in successfully or describe any error shown

---

## Notes

- **Never log the password** in memory files or daily notes
- If login fails, report the exact error message shown on screen
- If CAPTCHA appears, notify the user — do not attempt to solve it automatically
- The username field may auto-focus on page load; check before clicking
- If the Next button is not found, try pressing **Enter** after typing the username