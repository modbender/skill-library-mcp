import os
import sys
import json
import requests
import yaml
import subprocess
import argparse

# --- Configuration ---
# Standardize on CLOUDFLARE_* prefix
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN") or os.getenv("CF_API_TOKEN")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID") or os.getenv("CF_ZONE_ID")
CONFIG_PATH = "/etc/cloudflared/config.yml"

class CloudflareManager:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        } if CLOUDFLARE_API_TOKEN else None

    def _check_creds(self):
        if not self.headers or not CLOUDFLARE_ZONE_ID:
            return {"error": "Missing CLOUDFLARE_API_TOKEN or CLOUDFLARE_ZONE_ID."}
        return None

    def list_dns(self):
        if err := self._check_creds(): return err
        
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
        params = {"per_page": 100}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def add_dns(self, record_type, name, content, proxied=True, comment=""):
        if err := self._check_creds(): return err
        
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied,
            "comment": comment
        }
        if self.dry_run:
            return {"status": "dry-run", "action": "add_dns", "data": data}
            
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def update_dns(self, record_id, record_type, name, content, proxied=True, comment=""):
        if err := self._check_creds(): return err
        
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records/{record_id}"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied,
            "comment": comment
        }
        if self.dry_run:
            return {"status": "dry-run", "action": "update_dns", "data": data}

        response = requests.put(url, headers=self.headers, json=data)
        return response.json()

    def delete_dns(self, record_id):
        if err := self._check_creds(): return err
        
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records/{record_id}"
        
        if self.dry_run:
            return {"status": "dry-run", "action": "delete_dns", "url": url}

        response = requests.delete(url, headers=self.headers)
        return response.json()

    def update_setting(self, setting_id, value):
        if err := self._check_creds(): return err
        
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/settings/{setting_id}"
        data = {"value": value}
        
        if self.dry_run:
            return {"status": "dry-run", "action": "update_setting", "data": data}

        response = requests.patch(url, headers=self.headers, json=data)
        return response.json()

    def update_ingress(self, hostname, service):
        """
        Updates cloudflared config.
        REQUIRES: Sudo access on the host.
        Use --dry-run to preview changes without writing.
        """
        try:
            # Check if config exists, otherwise cannot proceed unless it's a dry run setup
            if not os.path.exists(CONFIG_PATH) and not self.dry_run:
                 return {"error": f"Config file not found at {CONFIG_PATH}"}

            # Read current config (requires read access, usually root/cloudflared user)
            # In a typical setup, 'cat' might need sudo if permissions are tight
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = yaml.safe_load(f)
            except PermissionError:
                # Try reading via sudo cat
                cmd = ["sudo", "cat", CONFIG_PATH]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                config = yaml.safe_load(result.stdout)

            if 'ingress' not in config:
                config['ingress'] = []

            # Check if hostname already exists
            exists = False
            for entry in config['ingress']:
                if entry.get('hostname') == hostname:
                    entry['service'] = service
                    exists = True
                    break
            
            if not exists:
                # Insert before the last catch-all entry if it exists
                if config['ingress'] and 'service' in config['ingress'][-1] and 'hostname' not in config['ingress'][-1]:
                    config['ingress'].insert(-1, {"hostname": hostname, "service": service})
                else:
                    config['ingress'].append({"hostname": hostname, "service": service})

            yaml_str = yaml.dump(config, default_flow_style=False)

            if self.dry_run:
                return {
                    "status": "dry-run", 
                    "action": "update_ingress", 
                    "file": CONFIG_PATH,
                    "new_content_preview": yaml_str
                }

            # Write back using sudo tee via subprocess
            process = subprocess.Popen(['sudo', 'tee', CONFIG_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            process.communicate(input=yaml_str.encode())
            
            # Restart cloudflared
            subprocess.run(['sudo', 'systemctl', 'restart', 'cloudflared'], check=True)
            return {"status": "success", "message": f"Updated ingress for {hostname} and restarted cloudflared."}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare Manager CLI")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without applying them")
    subparsers = parser.add_subparsers(dest="command")

    # List DNS
    subparsers.add_parser("list-dns")

    # Add DNS
    add_parser = subparsers.add_parser("add-dns")
    add_parser.add_argument("--type", required=True, choices=["A", "CNAME", "TXT", "MX"])
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--content", required=True)
    add_parser.add_argument("--comment", default="")
    add_parser.add_argument("--no-proxy", action="store_false", dest="proxied")

    # Update DNS
    up_parser = subparsers.add_parser("update-dns")
    up_parser.add_argument("--id", required=True)
    up_parser.add_argument("--type", required=True)
    up_parser.add_argument("--name", required=True)
    up_parser.add_argument("--content", required=True)
    up_parser.add_argument("--comment", default="")
    up_parser.add_argument("--no-proxy", action="store_false", dest="proxied")

    # Delete DNS
    del_parser = subparsers.add_parser("delete-dns")
    del_parser.add_argument("--id", required=True)

    # Update Zone Setting
    set_parser = subparsers.add_parser("update-setting")
    set_parser.add_argument("--id", required=True)
    set_parser.add_argument("--value", required=True)

    # Update Ingress
    ing_parser = subparsers.add_parser("update-ingress")
    ing_parser.add_argument("--hostname", required=True)
    ing_parser.add_argument("--service", required=True)

    args = parser.parse_args()
    manager = CloudflareManager(dry_run=args.dry_run)

    if args.command == "list-dns":
        print(json.dumps(manager.list_dns(), indent=2))
    elif args.command == "add-dns":
        print(json.dumps(manager.add_dns(args.type, args.name, args.content, args.proxied, args.comment), indent=2))
    elif args.command == "update-dns":
        print(json.dumps(manager.update_dns(args.id, args.type, args.name, args.content, args.proxied, args.comment), indent=2))
    elif args.command == "delete-dns":
        print(json.dumps(manager.delete_dns(args.id), indent=2))
    elif args.command == "update-setting":
        try:
            val = json.loads(args.value)
        except:
            val = args.value
        print(json.dumps(manager.update_setting(args.id, val), indent=2))
    elif args.command == "update-ingress":
        print(json.dumps(manager.update_ingress(args.hostname, args.service), indent=2))
    else:
        parser.print_help()
