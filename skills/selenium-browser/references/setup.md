# Selenium + Chrome Setup Guide

## Install Google Chrome
```
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Fedora
sudo dnf install -y google-chrome-stable
```

## Install ChromeDriver
```
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${CHROME_VERSION%.*}/chromedriver_linux64.zip"
wget -q $CHROMEDRIVER_URL -O /tmp/chromedriver.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin
chmod +x /usr/local/bin/chromedriver
```

## Install Selenium Python package
```
pip install --upgrade selenium
```

