#!/usr/bin/env python3
import os
import sys
import json
import re
import requests
import argparse
from typing import Optional, Dict, List, Any, Union
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NODE_RED_USER = os.getenv("NODE_RED_USERNAME") or os.getenv("NR_USER")
NODE_RED_PASS = os.getenv("NODE_RED_PASSWORD") or os.getenv("NR_PASS")
NODE_RED_URL = os.getenv("NODE_RED_URL") or os.getenv("NR_URL", "http://127.0.0.1:1880")
API_TIMEOUT = 30

class NodeRedAPIError(Exception):
    pass

class NodeRedAPI:
    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = base_url or NODE_RED_URL.rstrip('/')
        self.username = username or NODE_RED_USER
        self.password = password or NODE_RED_PASS
        self.token: Optional[str] = None
        
        if not self.username or not self.password:
            raise NodeRedAPIError("NODE_RED_USERNAME and NODE_RED_PASSWORD must be set")

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)
            elif method.upper() == "POST":
                resp = requests.post(url, headers=headers, json=json_data, data=data, timeout=API_TIMEOUT)
            elif method.upper() == "PUT":
                resp = requests.put(url, headers=headers, json=json_data, timeout=API_TIMEOUT)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=API_TIMEOUT)
            else:
                raise NodeRedAPIError(f"Unsupported HTTP method: {method}")
            
            if resp.status_code == 401:
                self.token = None
                self._get_headers()
                if method.upper() == "GET":
                    resp = requests.get(url, headers=self._get_headers(), params=params, timeout=API_TIMEOUT)
                elif method.upper() == "POST":
                    resp = requests.post(url, headers=self._get_headers(), json=json_data, data=data, timeout=API_TIMEOUT)
                elif method.upper() == "PUT":
                    resp = requests.put(url, headers=self._get_headers(), json=json_data, timeout=API_TIMEOUT)
                elif method.upper() == "DELETE":
                    resp = requests.delete(url, headers=self._get_headers(), timeout=API_TIMEOUT)
            
            if resp.status_code >= 400:
                error_msg = f"API error ({resp.status_code})"
                try:
                    error_data = resp.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                    elif "message" in error_data:
                        error_msg = error_data["message"]
                except:
                    error_msg = resp.text or error_msg
                raise NodeRedAPIError(error_msg)
            
            if resp.status_code == 204:
                return {}
            
            return resp.json()
            
        except requests.exceptions.Timeout:
            raise NodeRedAPIError("Request timed out. Node-RED may be unresponsive.")
        except requests.exceptions.ConnectionError:
            raise NodeRedAPIError(f"Could not connect to Node-RED at {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise NodeRedAPIError(f"Network error: {e}")

    def login(self) -> bool:
        url = f"{self.base_url}/auth/token"
        payload = {
            "client_id": "node-red-admin",
            "grant_type": "password",
            "scope": "*",
            "username": self.username,
            "password": self.password
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=API_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                return True
            return False
        except Exception as e:
            raise NodeRedAPIError(f"Login failed: {e}")

    def _get_headers(self) -> Dict[str, str]:
        if not self.token:
            if not self.login():
                raise NodeRedAPIError("Authentication failed. Check credentials.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _validate_flow_id(self, flow_id: str) -> None:
        if not flow_id or not isinstance(flow_id, str):
            raise ValueError("Flow ID must be a non-empty string")
        if not re.match(r'^[a-zA-Z0-9_-]+$', flow_id):
            raise ValueError("Flow ID contains invalid characters")

    def _validate_module_name(self, module: str) -> None:
        if not module or not isinstance(module, str):
            raise ValueError("Module name must be a non-empty string")
        if not re.match(r'^[@a-zA-Z0-9._/-]+$', module):
            raise ValueError("Module name contains invalid characters")

    def _validate_flow_json(self, flow_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        if isinstance(flow_data, dict):
            if "flows" in flow_data:
                flows = flow_data["flows"]
            else:
                flows = [flow_data]
        elif isinstance(flow_data, list):
            flows = flow_data
        else:
            raise ValueError("Flow data must be a dict or list")
        
        if not flows:
            raise ValueError("Flow data is empty")
        
        for flow in flows:
            if not isinstance(flow, dict):
                raise ValueError("Each flow must be a dictionary")
            if "id" not in flow and "type" not in flow:
                raise ValueError("Flow missing required fields: id or type")

    def list_flows(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/flows")

    def get_flow(self, flow_id: str) -> Dict[str, Any]:
        self._validate_flow_id(flow_id)
        return self._make_request("GET", f"/flow/{flow_id}")

    def deploy(self, flow_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        self._validate_flow_json(flow_data)
        
        if isinstance(flow_data, list):
            flow_data = {"flows": flow_data}
        elif isinstance(flow_data, dict) and "flows" not in flow_data:
            flow_data = {"flows": [flow_data]}
        
        return self._make_request("POST", "/flows", json_data=flow_data)

    def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_flow_id(flow_id)
        self._validate_flow_json(flow_data)
        return self._make_request("PUT", f"/flow/{flow_id}", json_data=flow_data)

    def delete_flow(self, flow_id: str) -> Dict[str, Any]:
        self._validate_flow_id(flow_id)
        return self._make_request("DELETE", f"/flow/{flow_id}")

    def get_flow_state(self) -> Dict[str, Any]:
        return self._make_request("GET", "/flows/state")

    def set_flow_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/flows/state", json_data=state_data)

    def list_nodes(self) -> Dict[str, Any]:
        return self._make_request("GET", "/nodes")

    def install_node(self, module: str) -> Dict[str, Any]:
        self._validate_module_name(module)
        return self._make_request("POST", "/nodes", json_data={"module": module})

    def get_node_info(self, module: str) -> Dict[str, Any]:
        self._validate_module_name(module)
        return self._make_request("GET", f"/nodes/{module}")

    def enable_node(self, module: str) -> Dict[str, Any]:
        self._validate_module_name(module)
        return self._make_request("PUT", f"/nodes/{module}", json_data={"enabled": True})

    def disable_node(self, module: str) -> Dict[str, Any]:
        self._validate_module_name(module)
        return self._make_request("PUT", f"/nodes/{module}", json_data={"enabled": False})

    def remove_node(self, module: str) -> Dict[str, Any]:
        self._validate_module_name(module)
        return self._make_request("DELETE", f"/nodes/{module}")

    def get_settings(self) -> Dict[str, Any]:
        return self._make_request("GET", "/settings")

    def get_diagnostics(self) -> Dict[str, Any]:
        return self._make_request("GET", "/diagnostics")

    def get_context(self, store: str, key: str) -> Any:
        if not store or not isinstance(store, str):
            raise ValueError("Store must be a non-empty string")
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")
        return self._make_request("GET", f"/context/{store}/{key}")

    def set_context(self, store: str, key: str, value: Any) -> Dict[str, Any]:
        if not store or not isinstance(store, str):
            raise ValueError("Store must be a non-empty string")
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")
        return self._make_request("POST", f"/context/{store}/{key}", json_data={"value": value})

    def backup_flows(self, output_file: Optional[str] = None) -> str:
        flows = self.list_flows()
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "flows": flows
        }
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"node-red-backup-{timestamp}.json"
        
        if not os.path.isabs(output_file):
            output_file = os.path.join(os.getcwd(), output_file)
        
        with open(output_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return output_file

    def restore_flows(self, backup_file: str) -> Dict[str, Any]:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(os.getcwd(), backup_file)
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        if isinstance(backup_data, dict) and "flows" in backup_data:
            flows = backup_data["flows"]
        elif isinstance(backup_data, list):
            flows = backup_data
        else:
            raise ValueError("Invalid backup file format")
        
        return self.deploy(flows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Node-RED Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Flows
    list_flows_parser = subparsers.add_parser("list-flows", help="List all flows")
    
    get_flow_parser = subparsers.add_parser("get-flow", help="Get specific flow by ID")
    get_flow_parser.add_argument("flow_id", help="Flow ID")
    
    deploy_parser = subparsers.add_parser("deploy", help="Deploy flows from file")
    deploy_parser.add_argument("--file", required=True, help="Path to flow JSON file")
    
    update_flow_parser = subparsers.add_parser("update-flow", help="Update specific flow")
    update_flow_parser.add_argument("flow_id", help="Flow ID")
    update_flow_parser.add_argument("--file", required=True, help="Path to flow JSON file")
    
    delete_flow_parser = subparsers.add_parser("delete-flow", help="Delete specific flow")
    delete_flow_parser.add_argument("flow_id", help="Flow ID")
    
    get_state_parser = subparsers.add_parser("get-flow-state", help="Get flow runtime state")
    
    set_state_parser = subparsers.add_parser("set-flow-state", help="Set flow runtime state")
    set_state_parser.add_argument("--file", required=True, help="Path to state JSON file")
    
    # Backup/Restore
    backup_parser = subparsers.add_parser("backup", help="Backup flows to file")
    backup_parser.add_argument("--output", help="Output file path (default: auto-generated)")
    
    restore_parser = subparsers.add_parser("restore", help="Restore flows from backup file")
    restore_parser.add_argument("backup_file", help="Path to backup JSON file")
    
    # Nodes
    list_nodes_parser = subparsers.add_parser("list-nodes", help="List installed nodes")
    
    install_node_parser = subparsers.add_parser("install-node", help="Install node module")
    install_node_parser.add_argument("module", help="Node module name (e.g., node-red-contrib-http-request)")
    
    get_node_parser = subparsers.add_parser("get-node", help="Get node module information")
    get_node_parser.add_argument("module", help="Node module name")
    
    enable_node_parser = subparsers.add_parser("enable-node", help="Enable node module")
    enable_node_parser.add_argument("module", help="Node module name")
    
    disable_node_parser = subparsers.add_parser("disable-node", help="Disable node module")
    disable_node_parser.add_argument("module", help="Node module name")
    
    remove_node_parser = subparsers.add_parser("remove-node", help="Remove node module")
    remove_node_parser.add_argument("module", help="Node module name")
    
    # Settings
    get_settings_parser = subparsers.add_parser("get-settings", help="Get runtime settings")
    
    get_diagnostics_parser = subparsers.add_parser("get-diagnostics", help="Get runtime diagnostics")
    
    # Context
    get_context_parser = subparsers.add_parser("get-context", help="Get context value")
    get_context_parser.add_argument("store", help="Context store (flow, global, etc.)")
    get_context_parser.add_argument("key", help="Context key")
    
    set_context_parser = subparsers.add_parser("set-context", help="Set context value")
    set_context_parser.add_argument("store", help="Context store (flow, global, etc.)")
    set_context_parser.add_argument("key", help="Context key")
    set_context_parser.add_argument("value", help="Context value (JSON string or plain text)")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        api = NodeRedAPI()
        
        if args.command == "list-flows":
            result = api.list_flows()
            print(json.dumps(result, indent=2))
        
        elif args.command == "get-flow":
            result = api.get_flow(args.flow_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "deploy":
            with open(args.file, 'r') as f:
                data = json.load(f)
            result = api.deploy(data)
            print(json.dumps(result, indent=2))
            print("Flows deployed successfully")
        
        elif args.command == "update-flow":
            with open(args.file, 'r') as f:
                data = json.load(f)
            result = api.update_flow(args.flow_id, data)
            print(json.dumps(result, indent=2))
            print(f"Flow {args.flow_id} updated successfully")
        
        elif args.command == "delete-flow":
            result = api.delete_flow(args.flow_id)
            print(json.dumps(result, indent=2))
            print(f"Flow {args.flow_id} deleted successfully")
        
        elif args.command == "get-flow-state":
            result = api.get_flow_state()
            print(json.dumps(result, indent=2))
        
        elif args.command == "set-flow-state":
            with open(args.file, 'r') as f:
                data = json.load(f)
            result = api.set_flow_state(data)
            print(json.dumps(result, indent=2))
            print("Flow state updated successfully")
        
        elif args.command == "backup":
            output_file = api.backup_flows(args.output)
            print(f"Backup saved to: {output_file}")
        
        elif args.command == "restore":
            result = api.restore_flows(args.backup_file)
            print(json.dumps(result, indent=2))
            print("Flows restored successfully")
        
        elif args.command == "list-nodes":
            result = api.list_nodes()
            print(json.dumps(result, indent=2))
        
        elif args.command == "install-node":
            result = api.install_node(args.module)
            print(json.dumps(result, indent=2))
            print(f"Node {args.module} installation initiated")
        
        elif args.command == "get-node":
            result = api.get_node_info(args.module)
            print(json.dumps(result, indent=2))
        
        elif args.command == "enable-node":
            result = api.enable_node(args.module)
            print(json.dumps(result, indent=2))
            print(f"Node {args.module} enabled")
        
        elif args.command == "disable-node":
            result = api.disable_node(args.module)
            print(json.dumps(result, indent=2))
            print(f"Node {args.module} disabled")
        
        elif args.command == "remove-node":
            result = api.remove_node(args.module)
            print(json.dumps(result, indent=2))
            print(f"Node {args.module} removed")
        
        elif args.command == "get-settings":
            result = api.get_settings()
            print(json.dumps(result, indent=2))
        
        elif args.command == "get-diagnostics":
            result = api.get_diagnostics()
            print(json.dumps(result, indent=2))
        
        elif args.command == "get-context":
            result = api.get_context(args.store, args.key)
            print(json.dumps(result, indent=2))
        
        elif args.command == "set-context":
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            result = api.set_context(args.store, args.key, value)
            print(json.dumps(result, indent=2))
            print(f"Context {args.store}/{args.key} set successfully")
        
    except NodeRedAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
