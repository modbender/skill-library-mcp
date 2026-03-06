## IMPORTANT !!!!
change ScanResult file extension from txt -> xlsx located in template

## 🔍 NPM & Node.js Vulnerability Scanner (OSV API)

A lightweight tool that scans your Node.js/NPM dependencies and Linux Packages for known vulnerabilities by using the **Google OSV API**. It reads your project packages and instantly returns any related CVEs.

### 🧠 How It Works
1. Reads `packages/package.json` / `packages/package.txt`
2. Collects all dependency names and versions
3. Sends them to the **OSV API**
4. Receives and displays any vulnerabilities (CVEs) affecting those packages

**Linux**

    - python3 -m venv .venv
    - pip install requests openpyxl
    - source .venv/bin/activate
    - copy packages.json to /packages folder and name it exactly like this 'packages.json' for nodejs otherwise for python use this command:
        - pip freeze > packages.txt
    - python3 scanner.py npm

**Windows**

    - python3 -m venv .venv
    - pip install requests openpyxl
    - ./.venv/Script/Activate.ps1
    - copy packages.json to /packages folder and name it exactly like this 'packages.json' for nodejs otherwise for python use this command:
        - pip freeze > packages.txt
    - python3 scanner.py npm
