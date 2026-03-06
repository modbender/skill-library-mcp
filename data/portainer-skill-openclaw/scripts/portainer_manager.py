# Portainer Manager Skill Backend

import requests
import os
import json
import sys
import traceback
import urllib3

# Attempt to get Portainer API URL from environment, default to https://localhost:9443/api
PORTAINER_API_URL = os.environ.get("PORTAINER_API_URL", "https://localhost:9443/api") 

# Suppress warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_portainer_api_token():
    token = os.environ.get("PORTAINER_API_TOKEN")
    if not token:
        raise ValueError("PORTAINER_API_TOKEN environment variable not set.")
    return token

def list_environments():
    print(f"Attempting to list Portainer environments via {PORTAINER_API_URL}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        response = requests.get(f"{PORTAINER_API_URL}/endpoints", headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        output_data = response.json()
        print(json.dumps(output_data, indent=2), flush=True)
        return output_data
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def list_stacks(environment_id=None):
    print(f"Executing list_stacks{' for environment ID: ' + str(environment_id) if environment_id else ''}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        response = requests.get(f"{PORTAINER_API_URL}/stacks", headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        stacks = response.json()
        if environment_id:
            env_id_int = int(environment_id)
            stacks = [s for s in stacks if s.get("EndpointId") == env_id_int]
        print(json.dumps(stacks, indent=2), flush=True)
        return stacks
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def inspect_stack(stack_id):
    print(f"Inspecting stack ID: {stack_id}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        response = requests.get(f"{PORTAINER_API_URL}/stacks/{stack_id}", headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        output_data = response.json()
        
        # Also fetch the stack file content if possible
        try:
            file_response = requests.get(f"{PORTAINER_API_URL}/stacks/{stack_id}/file", headers=headers, timeout=10, verify=False)
            if file_response.status_code == 200:
                output_data["StackFileContent"] = file_response.json().get("StackFileContent", "")
        except:
            pass

        print(json.dumps(output_data, indent=2), flush=True)
        return output_data
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def remove_stack(stack_id):
    print(f"Removing stack ID: {stack_id}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        response = requests.delete(f"{PORTAINER_API_URL}/stacks/{stack_id}", headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        print(f"Successfully removed stack {stack_id}.", flush=True)
        return {"status": "success"}
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def deploy_stack(name, stack_content, endpoint_id):
    print(f"Deploying stack '{name}' to environment ID {endpoint_id}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        url = f"{PORTAINER_API_URL}/stacks/create/standalone/string?endpointId={endpoint_id}"
        payload = {"name": name, "stackFileContent": stack_content, "env": []}
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        response.raise_for_status()
        output_data = response.json()
        print(json.dumps(output_data, indent=2), flush=True)
        return output_data
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def update_stack(stack_id, stack_content, endpoint_id, prune=False):
    print(f"Updating stack ID {stack_id}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        url = f"{PORTAINER_API_URL}/stacks/{stack_id}?endpointId={endpoint_id}"
        payload = {
            "stackFileContent": stack_content,
            "env": [],
            "prune": prune
        }
        response = requests.put(url, headers=headers, json=payload, timeout=30, verify=False)
        response.raise_for_status()
        output_data = response.json()
        print(json.dumps(output_data, indent=2), flush=True)
        return output_data
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

def execute_docker_command(environment_id, path, method="GET", payload=None):
    print(f"Executing Docker command on env {environment_id}: {method} {path}...", flush=True)
    try:
        token = get_portainer_api_token()
        headers = {"X-API-Key": token, "Content-Type": "application/json"}
        # Portainer proxies Docker API requests at /endpoints/{id}/docker/{path}
        url = f"{PORTAINER_API_URL}/endpoints/{environment_id}/docker{path}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=payload, timeout=10, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, json=payload, timeout=10, verify=False)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        
        try:
            output_data = response.json()
        except:
            output_data = {"status": "success", "text": response.text}
            
        print(json.dumps(output_data, indent=2), flush=True)
        return output_data
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    cmd = sys.argv[1]
    
    if cmd == "list_environments":
        list_environments()
    elif cmd == "list_stacks":
        env_id = sys.argv[2] if len(sys.argv) > 2 else None
        list_stacks(env_id)
    elif cmd == "inspect_stack":
        inspect_stack(sys.argv[2])
    elif cmd == "remove_stack":
        remove_stack(sys.argv[2])
    elif cmd == "deploy_stack":
        deploy_stack(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "update_stack":
        # usage: update_stack <id> <content> <endpoint_id>
        update_stack(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "execute_docker_command":
        # usage: execute_docker_command <env_id> <path> <method> <json_payload>
        env_id = sys.argv[2]
        path = sys.argv[3]
        method = sys.argv[4] if len(sys.argv) > 4 else "GET"
        payload = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
        execute_docker_command(env_id, path, method, payload)
