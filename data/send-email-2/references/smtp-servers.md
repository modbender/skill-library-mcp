# Common SMTP Server Configurations

## Gmail

- Server: `smtp.gmail.com`
- Port: `587` (TLS) or `465` (SSL)
- Requires App Password: https://myaccount.google.com/apppasswords
- Use: `--use-tls` for port 587, `--use-ssl` for port 465

## Outlook/Office 365

- Server: `smtp.office365.com`
- Port: `587` (TLS)
- No special setup required for standard accounts

## QQ Mail

- Server: `smtp.qq.com`
- Port: `587` (TLS) or `465` (SSL)
- Requires SMTP authorization code in account settings

## 126 Mail

- Server: `smtp.126.com`
- Port: `465` (SSL) or `25` (SSL)
- Requires SMTP authorization code (not login password)
- Get authorization code: Login → Settings → POP3/SMTP/IMAP → Enable SMTP

## 163 Mail

- Server: `smtp.163.com`
- Port: `465` (SSL) or `994` (SSL)
- Requires SMTP authorization code (not login password)

## SendGrid

- Server: `smtp.sendgrid.net`
- Port: `587` (TLS) or `465` (SSL)
- Use API key as password

## Mailgun

- Server: `smtp.mailgun.org`
- Port: `587` (TLS)
- Use SMTP credentials from Mailgun dashboard

## Aliyun

- Server: `smtp.aliyun.com`
- Port: `465` (SSL)
- Requires SMTP password in account settings
