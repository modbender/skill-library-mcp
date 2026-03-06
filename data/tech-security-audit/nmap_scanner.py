import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

def run_nmap_scan(target: str, scan_type: str = "vulnerability") -> Dict:
    """
    Execute an Nmap scan on the specified target.
    
    Args:
        target (str): IP address or hostname to scan
        scan_type (str): Type of scan to perform (vulnerability, service, os)
        
    Returns:
        dict: Scan results parsed from Nmap output
    """
    # Build command based on scan type
    if scan_type == "vulnerability":
        cmd = ["nmap", "-sV", "--script", "vuln", target, "-oX", "-"]
    elif scan_type == "service":
        cmd = ["nmap", "-sV", target, "-oX", "-"]
    elif scan_type == "os":
        cmd = ["nmap", "-O", target, "-oX", "-"]
    else:
        cmd = ["nmap", target, "-oX", "-"]
    
    try:
        # Run the scan
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return {"error": f"Nmap scan failed with return code {result.returncode}", "stderr": result.stderr}
            
        # Parse XML output
        root = ET.fromstring(result.stdout)
        return _parse_nmap_xml(root)
    except subprocess.TimeoutExpired:
        return {"error": "Nmap scan timed out"}
    except Exception as e:
        return {"error": f"Failed to run Nmap scan: {str(e)}"}

def _parse_nmap_xml(root: ET.Element) -> Dict:
    """
    Parse Nmap XML output into a structured dictionary.
    
    Args:
        root (ET.Element): Root element of Nmap XML output
        
    Returns:
        dict: Parsed scan results
    """
    results = {
        "hosts": [],
        "scan_stats": {}
    }
    
    # Extract scan statistics
    if root.tag == "nmaprun":
        results["scan_stats"] = {
            "scanner": root.get("scanner"),
            "version": root.get("version"),
            "start_time": root.get("start"),
            "args": root.get("args")
        }
    
    # Extract host information
    for host in root.findall("host"):
        host_info = {
            "ip": "",
            "hostname": "",
            "status": "",
            "services": [],
            "os": [],
            "vulnerabilities": []
        }
        
        # Get IP address
        addresses = host.findall("address")
        for addr in addresses:
            if addr.get("addrtype") == "ipv4":
                host_info["ip"] = addr.get("addr")
                
        # Get hostname
        hostnames = host.findall("hostnames/hostname")
        if hostnames:
            host_info["hostname"] = hostnames[0].get("name")
            
        # Get status
        status = host.find("status")
        if status is not None:
            host_info["status"] = status.get("state")
            
        # Get services
        ports = host.findall("ports/port")
        for port in ports:
            service_info = {
                "port": port.get("portid"),
                "protocol": port.get("protocol"),
                "state": "",
                "service": "",
                "version": ""
            }
            
            # Port state
            state_elem = port.find("state")
            if state_elem is not None:
                service_info["state"] = state_elem.get("state")
                
            # Service info
            service_elem = port.find("service")
            if service_elem is not None:
                service_info["service"] = service_elem.get("name")
                service_info["version"] = service_elem.get("version", "")
                
            host_info["services"].append(service_info)
            
        # Get OS information
        os_matches = host.findall("os/osmatch")
        for os_match in os_matches:
            os_info = {
                "name": os_match.get("name"),
                "accuracy": os_match.get("accuracy")
            }
            host_info["os"].append(os_info)
            
        # Get vulnerability information
        scripts = host.findall("hostscript/script")
        for script in scripts:
            if script.get("id") in ["vulners", "vuln"]:
                vuln_info = {
                    "script_id": script.get("id"),
                    "output": script.get("output")
                }
                host_info["vulnerabilities"].append(vuln_info)
                
        results["hosts"].append(host_info)
        
    return results