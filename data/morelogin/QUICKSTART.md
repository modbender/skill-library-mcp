# MoreLogin Skill Quick Start

## 🚀 5-Minute Quick Start

### 1) Install Dependencies

```bash
cd ~/.openclaw/workspace/skills/morelogin
npm install
```

### 2) Start MoreLogin Desktop

1. Open the MoreLogin desktop app
2. Ensure you are logged in
3. Verify Local API is available: `http://127.0.0.1:40000`

### 3) Browser Profile Quick Verification

```bash
# List profiles
node bin/morelogin.js browser list --page 1 --page-size 20

# Start a profile
node bin/morelogin.js browser start --env-id <envId>

# View running status (get debugPort)
node bin/morelogin.js browser status --env-id <envId>

# Clear local cache (specify at least one cache switch)
node bin/morelogin.js browser clear-cache --env-id <envId> --cookie true

# Clear cloud cache
node bin/morelogin.js browser clean-cloud-cache --env-id <envId> --cookie true --others true

# Close when done
node bin/morelogin.js browser close --env-id <envId>
```

### 4) CloudPhone Quick Verification

```bash
# List
node bin/morelogin.js cloudphone list --page 1 --page-size 20

# Query details (includes ADB info)
node bin/morelogin.js cloudphone info --id <cloudPhoneId>

# Query ADB connection params (for distinguishing device connection methods)
node bin/morelogin.js cloudphone adb-info --id <cloudPhoneId>

# Enable ADB
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable true
```

### 5) Proxy/Group/Tag Quick Verification

```bash
# Proxy
node bin/morelogin.js proxy list --page 1 --page-size 20

# Group
node bin/morelogin.js group list --page 1 --page-size 20

# Tag
node bin/morelogin.js tag list
```

---

## ⚡ Command Reference

Entry equivalence note: `openclaw morelogin ...` and `node bin/morelogin.js ...` are fully equivalent (same arguments, same behavior, same exit code).

```bash
# View help
node bin/morelogin.js help

# Browser
node bin/morelogin.js browser list
node bin/morelogin.js browser start --env-id <envId>
node bin/morelogin.js browser status --env-id <envId>
node bin/morelogin.js browser detail --env-id <envId>
node bin/morelogin.js browser clear-cache --env-id <envId> --cookie true
node bin/morelogin.js browser clean-cloud-cache --env-id <envId> --cookie true --others true
node bin/morelogin.js browser close --env-id <envId>

# CloudPhone
node bin/morelogin.js cloudphone list
node bin/morelogin.js cloudphone start --id <cloudPhoneId>
node bin/morelogin.js cloudphone stop --id <cloudPhoneId>
node bin/morelogin.js cloudphone info --id <cloudPhoneId>
node bin/morelogin.js cloudphone adb-info --id <cloudPhoneId>
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable true

# Proxy
node bin/morelogin.js proxy list
node bin/morelogin.js proxy add --payload '{"proxyIp":"1.2.3.4","proxyPort":8000,"proxyType":0,"proxyProvider":"0"}'
node bin/morelogin.js proxy update --payload '{"id":"<proxyId>","proxyIp":"5.6.7.8","proxyPort":9000}'
node bin/morelogin.js proxy delete --ids "<proxyId1>,<proxyId2>"

# Group
node bin/morelogin.js group create --name "Default-Group"
node bin/morelogin.js group edit --id "<groupId>" --name "Default-Group-New"
node bin/morelogin.js group delete --ids "<groupId1>,<groupId2>"

# Tag
node bin/morelogin.js tag create --name "vip"
node bin/morelogin.js tag edit --id "<tagId>" --name "vip-new"
node bin/morelogin.js tag delete --ids "<tagId1>,<tagId2>"

```

---

## 🔧 Troubleshooting

**Local API connection failed?**
```bash
node bin/morelogin.js browser list --page 1 --page-size 1
```

**Browser profile failed to start?**
```bash
# Check if ID is correct
node bin/morelogin.js browser list

# Check running status
node bin/morelogin.js browser status --env-id <envId>
```

**CloudPhone command failed?**
```bash
# View cloud phone details and current status
node bin/morelogin.js cloudphone info --id <cloudPhoneId>
```
---

## 📝 Next Steps

- Full documentation: `README.md`
- Skill documentation: `SKILL.md`
- Official API: <https://guide.morelogin.com/api-reference/local-api>
