---
name: remote-disk-mount
description: "Mount remote storage (SMB/CIFS, FTP, SFTP, WebDAV) as local
  directory. For Debian/Ubuntu Linux only. Triggered when user needs to: (1)
  mount Windows/Samba share, (2) mount FTP/SFTP server, (3) mount WebDAV
  storage, (4) map remote storage to local disk. NOTE: Requires user
  confirmation before running privileged commands. Does NOT support plaintext
  passwords on command line — use credential files or interactive prompts
  instead."
---


# Remote Disk Mount

> ⚠️ **Security Note**: This skill is for **Debian/Ubuntu Linux only**. Do NOT use on other OS without adaptation.

## ⚠️ Security Guidelines

1. **Never pass passwords on command line** — Use credential files or interactive prompts instead
2. **Confirm with user before running sudo commands** — Don't auto-execute privileged operations
3. **Use SSH keys for SFTP** — Avoid password-based authentication
4. **Mount untrusted storage with caution** — It can expose local files

---

## 🚀 Workflow

### Step 1: Collect Info (Ask User)

Ask the user for:
- **Protocol**: SMB / FTP / SFTP / WebDAV?
- **Server IP/hostname**: e.g., `192.168.1.100` or `nas.example.com`
- **Username**: (for SMB/FTP/SFTP)
- **Password**: (will be used interactively, never shown in commands)
- **Share name**: (for SMB only, e.g., `shared`)
- **Mount point name**: (optional, e.g., `nas`, `backup`)

> 💡 **Tip**: Ask one question at a time, wait for response. Don't assume any values.

### Step 2: Check Environment

Run this to check/install deps based on protocol:

```bash
# SMB
sudo apt install smbclient cifs-utils -y

# FTP
sudo apt install curlftpfs -y

# SFTP
sudo apt install sshfs -y

# WebDAV
sudo apt install cadaver davfs2 -y
```

### Step 3: Create Mount Point

```bash
mkdir -p ~/mount_<name>
```

---

## Protocol Details

### SMB/CIFS

**Credential file method:**
```bash
# 1. Create credential file
echo "username=$USERNAME" | sudo tee /root/.smbcredentials
echo "password=$PASSWORD" | sudo tee -a /root/.smbcredentials
sudo chmod 600 /root/.smbcredentials

# 2. Mount
sudo mount.cifs //SERVER_IP/share ~/mount_name -o credentials=/root/.smbcredentials,uid=1000,gid=1000
```

### FTP (curlftpfs)

**Interactive password (recommended):**
```bash
curlftpfs -o user=$USERNAME ftp://SERVER_IP/ ~/mount_name
# Password will be prompted interactively - never shown in command
```

### SFTP (SSHFS)

**Key-based auth (recommended):**
```bash
sshfs $USERNAME@SERVER_IP:/ ~/mount_name -o uid=1000,gid=1000
# Use -o identityfile=~/.ssh/id_rsa for key-based auth
```

### WebDAV

```bash
sudo mount -t davfs http://SERVER_IP/webdav /mnt/webdav -o uid=1000,gid=1000
# Password prompted interactively
```

---

## Unmount

```bash
sudo umount /mountpoint
# or for FUSE
sudo fusermount -u /mountpoint
```

---

## Checklist Before Running

- [ ] Confirm OS is Debian/Ubuntu
- [ ] Get user confirmation before sudo commands
- [ ] Verify remote server is trusted
- [ ] Use SSH keys for SFTP instead of passwords
- [ ] Delete credential files after use if sensitive
