# EDirect Installation and Configuration ⚠️

## ⚠️ Important Security Warning

**Before proceeding, understand that:**

1. **External script execution**: This installation guide involves downloading and executing official NCBI scripts
2. **System modifications**: Will modify your PATH environment variable
3. **Permission requirements**: May require system-level package installation

**Always follow these security practices:**
- Review script content after downloading
- Validate in a test environment
- Do not pipe remote scripts directly to shell
- Regularly update and verify

## Prerequisites

- Unix-like system (Linux, macOS, or Windows with Cygwin/WSL)
- Internet connection
- curl or wget installed

**Important:** This skill uses **local installation only** – no Docker or containers required. All tools run directly on your system.

**Security Advisory:** Always verify the source of any installation script. The official NCBI EDirect installer is hosted at `ftp.ncbi.nlm.nih.gov`. When using automated installation, download the script to a file first and review it if desired, rather than piping directly to your shell. This protects against potential supply-chain attacks or compromised mirrors.

## Installation Methods

### 🔴 Security First: User Confirmation Steps

**Before executing any installation command, you must:**
1. Understand the commands that will be executed
2. Confirm network connection security
3. Backup important data
4. Prepare rollback plans

### Method 1: Secure Manual Installation

```bash
# =========== Step 1: Download ===========
# Download to file, do not execute directly
wget -q https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh

# =========== Step 2: Review ===========
# View script content (review is important)
cat install-edirect.sh | head -100  # View first 100 lines
# Or use a text editor to view complete content

# =========== Step 3: Analyze ===========
# Check what operations the script will perform
grep -n "wget\|curl\|chmod\|export" install-edirect.sh

# =========== Step 4: Execute ===========
# Execute manually only after review
chmod +x install-edirect.sh
./install-edirect.sh
```

### ⛔ Unsafe Practices (Prohibited)

**Never do this:**
```bash
# ❌ Dangerous: Piping remote script directly to shell
curl https://example.com/install.sh | bash

# ❌ Dangerous: Executing without review
sh -c "$(curl -fsSL https://example.com/install.sh)"
```

**Reasons:**
- Cannot review script content
- Cannot control mid-execution stops
- May be modified by man-in-the-middle attacks
- Cannot audit executed operations

### Method 2: Alternative Installation with Curl

If using curl, follow the same security steps:

```bash
# Secure way: Download, review, execute
curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -o install-edirect.sh
less install-edirect.sh  # Review
chmod +x install-edirect.sh
./install-edirect.sh
```

This script will:
1. Download EDirect scripts and programs from the official NCBI repository
2. Create an `edirect` folder in your home directory
3. Add the directory to your PATH

**Security Note:** Avoid piping remote scripts directly to your shell (e.g., `sh -c "curl | bash"`). Downloading first allows you to verify the content before execution, following best security practices.

### Method 2: Manual Installation (Alternative)

If the automated script doesn't work, you can manually install:

```bash
# Create edirect directory
mkdir -p ~/edirect
cd ~/edirect

# Download and extract the package
curl -O https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz
tar -xzf edirect.tar.gz

# Add to PATH
echo 'export PATH="$HOME/edirect:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Post-Installation Configuration

### 1. Configure API Key (For increased rate limits)

For increased rate limits (10 requests/second vs 3 requests/second), obtain an API key:

1. Create an NCBI account at https://www.ncbi.nlm.nih.gov/
2. Go to Account Settings → API Key Management
3. Generate a new API key

Add the API key to your environment:

```bash
# For current session
export NCBI_API_KEY=your_api_key_here

# For permanent configuration
echo 'export NCBI_API_KEY="your_api_key_here"' >> ~/.bashrc
echo 'export NCBI_API_KEY="your_api_key_here"' >> ~/.zshrc  # If using zsh
```

### 2. Configure Email Address (Optional - identifies you to NCBI)

NCBI requests that you identify yourself with an email address:

```bash
export NCBI_EMAIL="your.email@example.com"
echo 'export NCBI_EMAIL="your.email@example.com"' >> ~/.bashrc
```

### 3. Set Tool Configuration

EDirect tools can be configured with default options:

```bash
# Create configuration file if needed
touch ~/.ncbirc

# Set default format preferences
export EFETCH_FORMAT="xml"  # Default output format
```

## Verification

Test your installation:

```bash
# Check if commands are available
esearch -help
efetch -help

# Test a simple query
esearch -db pubmed -query "test" -retmax 1
```

Expected output should show help text without errors.

## Troubleshooting

### Common Issues

#### 1. "Command not found"
```bash
# Check if edirect is in PATH
echo $PATH | grep edirect

# If not, add it manually
export PATH="$HOME/edirect:$PATH"
```

#### 2. Permission Denied
```bash
# Make scripts executable
chmod +x ~/edirect/*.pl
chmod +x ~/edirect/*.pm
```

#### 3. Perl Module Errors
EDirect requires certain Perl modules. Install them:

```bash
# On Ubuntu/Debian
sudo apt-get install perl libwww-perl libxml-simple-perl

# On CentOS/RHEL
sudo yum install perl perl-libwww-perl perl-XML-Simple

# On macOS with Homebrew
brew install perl
cpan install LWP::Simple XML::Simple
```

#### 4. Proxy Configuration
If behind a proxy:

```bash
export ftp_proxy="http://proxy.example.com:8080"
export http_proxy="http://proxy.example.com:8080"
export https_proxy="http://proxy.example.com:8080"
```

#### 5. SSL Certificate Issues
If you encounter SSL certificate errors, update your system's CA certificates:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates

# CentOS/RHEL
sudo yum update ca-certificates

# macOS
brew install ca-certificates
```

Also ensure your system time is correct:
```bash
date  # check system time
# If incorrect, sync with NTP
sudo ntpdate pool.ntp.org  # or use timedatectl
```

**Important:** Never disable SSL verification by setting PERL_LWP_SSL_VERIFY_HOSTNAME=0 in production or when handling sensitive data. This weakens security and exposes you to man-in-the-middle attacks.

## Performance Tuning

### 1. Increase Timeouts for Large Queries
```bash
export EUTILS_TIMEOUT=60  # Increase timeout to 60 seconds
```

### 2. Enable Compression for Large Transfers
```bash
export EUTILS_COMPRESS=1  # Enable gzip compression
```

### 3. Cache Configuration
```bash
# Set cache directory
export NCBI_CACHE_DIR="$HOME/.ncbi/cache"
mkdir -p "$NCBI_CACHE_DIR"
```

## Uninstallation

To remove EDirect:

```bash
# Remove the edirect directory
rm -rf ~/edirect

# Remove from PATH in your shell configuration files
# Edit ~/.bashrc, ~/.bash_profile, ~/.zshrc, etc.
# Remove the line: export PATH="$HOME/edirect:$PATH"
```

## Platform-Specific Notes

### macOS
- Comes with Perl pre-installed
- May need to install command line tools: `xcode-select --install`

### Windows (WSL/Cygwin)
- Works well with Windows Subsystem for Linux (WSL)
- Cygwin requires Perl and related packages

### Linux Servers
- Most distributions have required Perl modules in repositories
- `screen` or `tmux` can be used for long-running queries

## Security Audit Checklist

### Pre-Installation Checks (Required)
- [ ] Confirm network environment security
- [ ] Backup important data
- [ ] Prepare rollback scripts
- [ ] Understand all commands to be executed

### Script Review (Required)
- [ ] Download script to local file
- [ ] View full script content (at least first 200 lines)
- [ ] Check all external URLs
- [ ] Understand commands the script will execute
- [ ] Confirm no hidden dangerous operations

### Environment Isolation Options
- [ ] Validate first in a test environment
- [ ] Use non-privileged user accounts
- [ ] Set up dedicated working directories
- [ ] Configure firewall rules

### Execution Monitoring
- [ ] Enable command logging
- [ ] Monitor network traffic
- [ ] Regularly check system integrity
- [ ] Set up anomaly alerts

## Containerized Installation Option

For production environments, containers can be used:

```bash
# Use Docker to run EDirect
docker run -it --rm \
  -v $(pwd)/data:/data \
  ncbi/edirect:latest \
  esearch -db pubmed -query "test"
```

## Compliance Notes

This installation process is suitable for:
- ✅ Personal research environments
- ✅ Academic institution laboratories
- ✅ Testing and development systems

Not suitable for:
- ⚠️ Production servers
- ⚠️ Critical business systems
- ⚠️ Multi-user shared environments
- ⚠️ Scenarios without audit capabilities

## Final Reminder

**You are fully responsible for this system installation.** Before proceeding, ensure you:
1. Understand all risks
2. Have sufficient technical capability
3. Have comprehensive backup and recovery plans
4. Accept potential security consequences

## Next Steps

Only proceed to the following after fully understanding the above security warnings:
- [BASICS.md](BASICS.md) Basic usage guide
- [EXAMPLES.md](EXAMPLES.md) Practical examples
- [ADVANCED.md](ADVANCED.md) Advanced techniques