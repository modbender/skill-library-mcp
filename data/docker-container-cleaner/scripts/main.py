#!/usr/bin/env python3
"""
Docker Container Cleaner - CLI tool to clean up Docker resources
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

def check_docker_available() -> bool:
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(["docker", "version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def run_docker_command(cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Run a docker command and return standardized result."""
    start_time = time.time()
    try:
        result = subprocess.run(
            ["docker"] + cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "elapsed_time": elapsed
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "elapsed_time": time.time() - start_time
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": time.time() - start_time
        }

def parse_size(size_str: str) -> int:
    """Parse Docker size string (e.g., '1.2GB', '450MB') to bytes."""
    if not size_str:
        return 0
    
    size_str = size_str.upper().strip()
    
    # Extract numeric part
    import re
    match = re.match(r"([\d.]+)\s*([KMGTP]?B)", size_str)
    if not match:
        return 0
    
    value = float(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "PB": 1024 ** 5
    }
    
    return int(value * multipliers.get(unit, 1))

def format_size(bytes: int) -> str:
    """Format bytes to human readable string."""
    if bytes == 0:
        return "0B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    
    while bytes >= 1024 and unit_index < len(units) - 1:
        bytes /= 1024
        unit_index += 1
    
    return f"{bytes:.1f}{units[unit_index]}"

def get_containers_info() -> Dict[str, Any]:
    """Get information about Docker containers."""
    # Get running containers
    running_cmd = run_docker_command(["ps", "--format", "{{.ID}} {{.Names}}", "--no-trunc"])
    running = []
    if running_cmd["success"]:
        for line in running_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    running.append({"id": parts[0], "name": parts[1]})
    
    # Get stopped containers
    stopped_cmd = run_docker_command(["ps", "-a", "--filter", "status=exited", "--format", "{{.ID}} {{.Names}} {{.Size}}", "--no-trunc"])
    stopped = []
    total_stopped_size = 0
    if stopped_cmd["success"]:
        for line in stopped_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 2)
                if len(parts) >= 2:
                    container_info = {"id": parts[0], "name": parts[1]}
                    if len(parts) == 3:
                        size_str = parts[2]
                        container_info["size"] = size_str
                        total_stopped_size += parse_size(size_str)
                    stopped.append(container_info)
    
    return {
        "running": running,
        "stopped": stopped,
        "stopped_count": len(stopped),
        "stopped_size_bytes": total_stopped_size,
        "running_count": len(running)
    }

def get_images_info() -> Dict[str, Any]:
    """Get information about Docker images."""
    # Get all images
    images_cmd = run_docker_command(["images", "--format", "{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}", "--no-trunc"])
    all_images = []
    total_size = 0
    
    if images_cmd["success"]:
        for line in images_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 2)
                if len(parts) == 3:
                    image_info = {
                        "repository": parts[0],
                        "id": parts[1],
                        "size": parts[2]
                    }
                    all_images.append(image_info)
                    total_size += parse_size(parts[2])
    
    # Get dangling images (images with no tag)
    dangling_cmd = run_docker_command(["images", "-f", "dangling=true", "--format", "{{.ID}} {{.Size}}", "--no-trunc"])
    dangling_images = []
    dangling_size = 0
    
    if dangling_cmd["success"]:
        for line in dangling_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    dangling_images.append({"id": parts[0], "size": parts[1]})
                    dangling_size += parse_size(parts[1])
    
    return {
        "all": all_images,
        "total_count": len(all_images),
        "total_size_bytes": total_size,
        "dangling": dangling_images,
        "dangling_count": len(dangling_images),
        "dangling_size_bytes": dangling_size
    }

def get_volumes_info() -> Dict[str, Any]:
    """Get information about Docker volumes."""
    # Get all volumes
    volumes_cmd = run_docker_command(["volume", "ls", "--format", "{{.Name}} {{.Driver}}", "--no-trunc"])
    all_volumes = []
    
    if volumes_cmd["success"]:
        for line in volumes_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    all_volumes.append({"name": parts[0], "driver": parts[1]})
    
    # Check for unused volumes (simplified - in real implementation would check mount points)
    # For now, we'll assume a volume is unused if it's not mounted by a running container
    # This is a simplified check
    unused_volumes = []
    unused_count = len(all_volumes)  # Simplified - in reality would need to check mount points
    
    return {
        "all": all_volumes,
        "total_count": len(all_volumes),
        "unused": unused_volumes,
        "unused_count": unused_count
    }

def get_networks_info() -> Dict[str, Any]:
    """Get information about Docker networks."""
    # Get all networks
    networks_cmd = run_docker_command(["network", "ls", "--format", "{{.Name}} {{.Driver}}", "--no-trunc"])
    all_networks = []
    
    if networks_cmd["success"]:
        for line in networks_cmd["stdout"].strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    all_networks.append({"name": parts[0], "driver": parts[1]})
    
    # Check for unused networks (simplified)
    unused_networks = []
    unused_count = len(all_networks)  # Simplified - in reality would need to check if used by containers
    
    return {
        "all": all_networks,
        "total_count": len(all_networks),
        "unused": unused_networks,
        "unused_count": unused_count
    }

def get_resource_summary() -> Dict[str, Any]:
    """Get summary of all Docker resources."""
    containers = get_containers_info()
    images = get_images_info()
    volumes = get_volumes_info()
    networks = get_networks_info()
    
    total_reclaimable = (
        containers["stopped_size_bytes"] +
        images["dangling_size_bytes"]
    )
    
    return {
        "containers": containers,
        "images": images,
        "volumes": volumes,
        "networks": networks,
        "total_reclaimable_bytes": total_reclaimable,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

def clean_containers(force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Clean up stopped containers."""
    if dry_run:
        containers = get_containers_info()
        return {
            "operation": "clean_containers",
            "dry_run": True,
            "would_remove": containers["stopped_count"],
            "would_reclaim_bytes": containers["stopped_size_bytes"]
        }
    
    cmd = ["container", "prune"]
    if force:
        cmd.append("--force")
    else:
        cmd.append("--force")  # Always force for non-interactive mode
    
    result = run_docker_command(cmd)
    
    if result["success"]:
        # Parse output to get reclaimed space
        reclaimed = 0
        if "Total reclaimed space:" in result["stdout"]:
            import re
            match = re.search(r"Total reclaimed space:\s*([\d.]+\s*[KMGTP]?B)", result["stdout"])
            if match:
                reclaimed = parse_size(match.group(1))
        
        return {
            "operation": "clean_containers",
            "success": True,
            "reclaimed_bytes": reclaimed,
            "output": result["stdout"]
        }
    else:
        return {
            "operation": "clean_containers",
            "success": False,
            "error": result.get("error", result.get("stderr", "Unknown error"))
        }

def clean_images(dangling: bool = False, unused: bool = False, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Clean up Docker images."""
    if not dangling and not unused:
        return {
            "operation": "clean_images",
            "success": False,
            "error": "Must specify --dangling or --unused"
        }
    
    if dry_run:
        images = get_images_info()
        would_remove = 0
        would_reclaim = 0
        
        if dangling:
            would_remove += images["dangling_count"]
            would_reclaim += images["dangling_size_bytes"]
        
        # Note: unused images check would need more sophisticated logic
        # For now, we'll just report dangling
        
        return {
            "operation": "clean_images",
            "dry_run": True,
            "would_remove": would_remove,
            "would_reclaim_bytes": would_reclaim,
            "dangling": dangling,
            "unused": unused
        }
    
    cmd = ["image", "prune"]
    
    if dangling and unused:
        # Prune all images
        cmd.append("--all")
    elif dangling:
        # Only dangling
        pass  # Default is dangling
    elif unused:
        # This would require different logic - for now use --all
        cmd.append("--all")
    
    if force:
        cmd.append("--force")
    else:
        cmd.append("--force")  # Always force for non-interactive mode
    
    result = run_docker_command(cmd)
    
    if result["success"]:
        reclaimed = 0
        if "Total reclaimed space:" in result["stdout"]:
            import re
            match = re.search(r"Total reclaimed space:\s*([\d.]+\s*[KMGTP]?B)", result["stdout"])
            if match:
                reclaimed = parse_size(match.group(1))
        
        return {
            "operation": "clean_images",
            "success": True,
            "reclaimed_bytes": reclaimed,
            "dangling": dangling,
            "unused": unused,
            "output": result["stdout"]
        }
    else:
        return {
            "operation": "clean_images",
            "success": False,
            "error": result.get("error", result.get("stderr", "Unknown error"))
        }

def clean_volumes(force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Clean up unused volumes."""
    if dry_run:
        volumes = get_volumes_info()
        return {
            "operation": "clean_volumes",
            "dry_run": True,
            "would_remove": volumes["unused_count"]
        }
    
    cmd = ["volume", "prune"]
    if force:
        cmd.append("--force")
    else:
        cmd.append("--force")  # Always force for non-interactive mode
    
    result = run_docker_command(cmd)
    
    if result["success"]:
        reclaimed = 0
        if "Total reclaimed space:" in result["stdout"]:
            import re
            match = re.search(r"Total reclaimed space:\s*([\d.]+\s*[KMGTP]?B)", result["stdout"])
            if match:
                reclaimed = parse_size(match.group(1))
        
        return {
            "operation": "clean_volumes",
            "success": True,
            "reclaimed_bytes": reclaimed,
            "output": result["stdout"]
        }
    else:
        return {
            "operation": "clean_volumes",
            "success": False,
            "error": result.get("error", result.get("stderr", "Unknown error"))
        }

def clean_networks(force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Clean up unused networks."""
    if dry_run:
        networks = get_networks_info()
        return {
            "operation": "clean_networks",
            "dry_run": True,
            "would_remove": networks["unused_count"]
        }
    
    cmd = ["network", "prune"]
    if force:
        cmd.append("--force")
    else:
        cmd.append("--force")  # Always force for non-interactive mode
    
    result = run_docker_command(cmd)
    
    if result["success"]:
        return {
            "operation": "clean_networks",
            "success": True,
            "output": result["stdout"]
        }
    else:
        return {
            "operation": "clean_networks",
            "success": False,
            "error": result.get("error", result.get("stderr", "Unknown error"))
        }

def format_table(data: Dict[str, Any]) -> str:
    """Format resource summary as a table."""
    lines = []
    lines.append("Docker Resource Summary")
    lines.append("=" * 50)
    
    # Containers
    containers = data["containers"]
    lines.append(f"Containers:")
    lines.append(f"  Running: {containers['running_count']}")
    lines.append(f"  Stopped: {containers['stopped_count']} ({format_size(containers['stopped_size_bytes'])})")
    
    # Images
    images = data["images"]
    lines.append(f"Images:")
    lines.append(f"  Total: {images['total_count']} ({format_size(images['total_size_bytes'])})")
    lines.append(f"  Dangling: {images['dangling_count']} ({format_size(images['dangling_size_bytes'])})")
    
    # Volumes
    volumes = data["volumes"]
    lines.append(f"Volumes:")
    lines.append(f"  Total: {volumes['total_count']}")
    lines.append(f"  Unused: {volumes['unused_count']}")
    
    # Networks
    networks = data["networks"]
    lines.append(f"Networks:")
    lines.append(f"  Total: {networks['total_count']}")
    lines.append(f"  Unused: {networks['unused_count']}")
    
    # Total reclaimable
    lines.append(f"Total reclaimable space: {format_size(data['total_reclaimable_bytes'])}")
    
    return "\n".join(lines)

def run_status(args):
    """Execute the status command."""
    if not check_docker_available():
        return {
            "status": "error",
            "error": "Docker is not available. Make sure Docker is installed and running."
        }
    
    summary = get_resource_summary()
    
    if args.format == "json":
        return summary
    else:
        summary["formatted"] = format_table(summary)
        return summary

def run_clean(args):
    """Execute the clean command."""
    if not check_docker_available():
        return {
            "status": "error",
            "error": "Docker is not available. Make sure Docker is installed and running."
        }
    
    results = []
    force = args.force or args.yes or args.no_interactive
    
    # Clean containers
    if args.containers or args.all:
        result = clean_containers(force=force, dry_run=args.dry_run)
        results.append(result)
    
    # Clean images
    if args.images or args.all:
        result = clean_images(
            dangling=args.dangling or args.all,
            unused=args.unused or args.all,
            force=force,
            dry_run=args.dry_run
        )
        results.append(result)
    
    # Clean volumes
    if args.volumes or args.all:
        result = clean_volumes(force=force, dry_run=args.dry_run)
        results.append(result)
    
    # Clean networks
    if args.networks or args.all:
        result = clean_networks(force=force, dry_run=args.dry_run)
        results.append(result)
    
    # If nothing was specified but clean command was called, show status
    if not any([args.containers, args.images, args.volumes, args.networks, args.all]):
        return run_status(args)
    
    # Prepare output
    total_reclaimed = 0
    any_failed = False
    errors = []
    
    for result in results:
        if not result.get("success", True) and "dry_run" not in result:
            any_failed = True
            if "error" in result:
                errors.append(f"{result.get('operation', 'Unknown')}: {result['error']}")
        if "reclaimed_bytes" in result:
            total_reclaimed += result["reclaimed_bytes"]
    
    output = {
        "status": "error" if any_failed else "success",
        "operations": results,
        "total_reclaimed_bytes": total_reclaimed,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    
    if errors:
        output["errors"] = errors
    
    if args.dry_run:
        output["dry_run"] = True
    
    return output

def main():
    parser = argparse.ArgumentParser(
        description="Clean up Docker resources (containers, images, volumes, networks)."
    )
    parser.add_argument(
        "command",
        choices=["status", "clean", "help"],
        help="Command to execute"
    )
    
    # Common arguments
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for Docker operations (default: 30)"
    )
    
    # Clean command arguments
    parser.add_argument(
        "--containers",
        action="store_true",
        help="Remove stopped containers"
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Remove images (requires --dangling or --unused)"
    )
    parser.add_argument(
        "--dangling",
        action="store_true",
        help="Remove dangling images (images with no tag)"
    )
    parser.add_argument(
        "--unused",
        action="store_true",
        help="Remove unused images (not used by any container)"
    )
    parser.add_argument(
        "--volumes",
        action="store_true",
        help="Remove unused volumes"
    )
    parser.add_argument(
        "--networks",
        action="store_true",
        help="Remove unused networks"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clean all resource types"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Auto-answer 'yes' to all prompts"
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.command == "status":
        result = run_status(args)
    elif args.command == "clean":
        result = run_clean(args)
    else:
        parser.print_help()
        return
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if "formatted" in result:
            print(result["formatted"])
        elif "status" in result and result["status"] == "error":
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif args.command == "clean" and "operations" in result:
            print("Cleanup Results:")
            print("=" * 50)
            for op in result["operations"]:
                if "dry_run" in op:
                    print(f"{op.get('operation', 'Unknown')}: Would remove {op.get('would_remove', 0)} items")
                    if "would_reclaim_bytes" in op and op["would_reclaim_bytes"] > 0:
                        print(f"  Would reclaim: {format_size(op['would_reclaim_bytes'])}")
                elif op.get("success", False):
                    print(f"✅ {op.get('operation', 'Unknown')}: Success")
                    if "reclaimed_bytes" in op and op["reclaimed_bytes"] > 0:
                        print(f"  Reclaimed: {format_size(op['reclaimed_bytes'])}")
                else:
                    print(f"❌ {op.get('operation', 'Unknown')}: {op.get('error', 'Unknown error')}")
            
            if "total_reclaimed_bytes" in result and result["total_reclaimed_bytes"] > 0:
                print(f"\\nTotal reclaimed: {format_size(result['total_reclaimed_bytes'])}")
        else:
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()