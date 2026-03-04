import argparse
import hashlib
import json
import subprocess
import sys
import os
import urllib.request

# OPSIN v2.8.0 — verified via SHA-256 checksum
OPSIN_URL = "https://github.com/dan2097/opsin/releases/download/2.8.0/opsin-cli-2.8.0-jar-with-dependencies.jar"
OPSIN_SHA256 = "d25bc08f41b8f6fcd6f35e18ab83f3b8d9218cdb003d55c5f74aaefe2e0c68ab"

def verify_jar(path, expected_sha256):
    """Verify JAR integrity via SHA-256 checksum."""
    if expected_sha256 is None:
        return True  # checksum not yet pinned
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_sha256

def ensure_opsin(jar_path):
    """Download OPSIN JAR if missing, with checksum verification."""
    if os.path.exists(jar_path):
        if not verify_jar(jar_path, OPSIN_SHA256):
            print(json.dumps({"error": "opsin.jar checksum mismatch — possible tampering. Delete and re-run to re-download."}), file=sys.stderr)
            sys.exit(1)
        return
    print(f"Downloading OPSIN from {OPSIN_URL}...", file=sys.stderr)
    urllib.request.urlretrieve(OPSIN_URL, jar_path)
    if not verify_jar(jar_path, OPSIN_SHA256):
        os.remove(jar_path)
        print(json.dumps({"error": "Downloaded opsin.jar failed checksum verification — removed."}), file=sys.stderr)
        sys.exit(1)
    print("OPSIN downloaded and verified.", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="OPSIN IUPAC name to SMILES")
    parser.add_argument("--name", required=True, help="IUPAC/systematic name")
    parser.add_argument("--output", help="Output SMILES file")
    args = parser.parse_args()

    jar_path = os.path.join(os.path.dirname(__file__), "opsin.jar")
    ensure_opsin(jar_path)

    cmd = ["java", "-jar", jar_path, "--stdin", "--output", "smiles"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate(input=args.name)
    if proc.returncode != 0:
        print(json.dumps({"error": stderr.strip()}), file=sys.stderr)
        sys.exit(1)
    
    smiles = stdout.strip()
    result = {"name": args.name, "smiles": smiles}
    print(json.dumps(result))
    if args.output:
        with open(args.output, 'w') as f:
            f.write(smiles)

if __name__ == "__main__":
    main()