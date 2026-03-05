import nmap
import json
import sys
import ipaddress
import subprocess

def is_valid_ipv4_address(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

def is_valid_cidr(cidr):
    try:
        ipaddress.ip_network(cidr)
        return True
    except ValueError:
        return False

def scan_network(target, ports, quick=False, fast=False, timeout=30, top_ports=None, hosts_limit=None, exclude=None):
    try:
        scanner = nmap.PortScanner()
    except nmap.PortScannerError:
        return {"error": "nmap program was not found. Please install nmap."}
    scan_options = '-sV'
    if fast:
        scan_options += ' -T4'
    if timeout:
        scan_options += f' --host-timeout {timeout}s'

    if top_ports:
        scan_options += f' --top-ports {top_ports}'

    if hosts_limit:
        scan_options += f' -n --max-hosts {hosts_limit}'

    if exclude:
        scan_options += f' --exclude {exclude}'


    try:
        if is_valid_ipv4_address(target):
            results = scanner.scan(target, ports, arguments=scan_options)
        elif is_valid_cidr(target):
            if not top_ports:
               scan_options += f' --top-ports 10' # default --quick for CIDR
            results = scanner.scan(target, ports, arguments=scan_options)
        elif '-' in target:
            start_ip, end_ip = target.split('-')
            results = scanner.scan(start_ip+'-'+end_ip, ports, arguments=scan_options)
        elif ',' in target:
             results = scanner.scan(target, ports, arguments=scan_options)

        else:
            return {"error": "Invalid target format. Supported formats: CIDR, range (start-end), single IP or comma-separated list."}
    except Exception as e:
        return {"error": str(e)}

    scan_data = {}
    if 'scan' in results:
        for host, host_data in results['scan'].items():
            scan_data[host] = {}
            if 'tcp' in host_data:
                scan_data[host]['tcp'] = host_data['tcp']

    return {"scan_results": scan_data, "nmap_command":scanner.command_line(), "scan_info": scanner.scaninfo()}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments. Usage: network-scan target=<target> ports=<ports> [--quick] [--fast] [--timeout <seconds>] [--top-ports <num>] [--hosts-limit <num>] [--exclude <ip>]"}, indent=4))
        sys.exit(1)

    target = None
    ports = None
    quick = False
    fast = False
    timeout = 30
    top_ports = None
    hosts_limit = None
    exclude = None

    try:
        for arg in sys.argv[1:]:
            if arg.startswith("target="):
                target = arg.split("=")[1]
            elif arg.startswith("ports="):
                ports = arg.split("=")[1]
            elif arg == "--quick":
                quick = True
            elif arg == "--fast":
                fast = True
            elif arg.startswith("--timeout="):
                timeout = int(arg.split("=")[1])
            elif arg.startswith("--top-ports="):
                top_ports = int(arg.split("=")[1])
            elif arg.startswith("--hosts-limit="):
                hosts_limit = int(arg.split("=")[1])
            elif arg.startswith("--exclude="):
                exclude = arg.split("=")[1]
    except Exception as e:
        print(json.dumps({"error": f"Error parsing arguments: {str(e)}"}))
        sys.exit(1)

    if not target or not ports:
        print(json.dumps({"error": "Target and ports are required arguments."}))
        sys.exit(1)

    results = scan_network(target, ports, quick, fast, timeout, top_ports, hosts_limit, exclude)
    print(json.dumps(results, indent=4))
