#!/usr/bin/env python3
"""
Test script for the tech-security-audit skill.
This script tests the framework without requiring actual Nmap installation.
"""

import sys
import os

# Add the tech-security-audit directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from nmap_scanner import _parse_nmap_xml
import xml.etree.ElementTree as ET

def test_parser_with_sample_data():
    """Test the Nmap XML parser with sample data."""
    print("Testing Nmap XML parser with sample data...")
    
    # Sample Nmap XML output
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV example.com" start="1234567890">
    <scaninfo type="syn" protocol="tcp"/>
    <host>
        <status state="up"/>
        <address addr="192.168.1.100" addrtype="ipv4"/>
        <hostnames>
            <hostname name="example.local" type="user"/>
        </hostnames>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh" version="OpenSSH 7.9"/>
            </port>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" version="Apache httpd 2.4.41"/>
            </port>
        </ports>
        <hostscript>
            <script id="vulners" output="CVE-2020-1234 7.5 Medium&#xa;CVE-2019-5678 5.0 Medium"/>
        </hostscript>
    </host>
    <runstats>
        <finished time="1234567900"/>
    </runstats>
</nmaprun>"""
    
    try:
        root = ET.fromstring(sample_xml)
        results = _parse_nmap_xml(root)
        
        print("Parser test successful!")
        print(f"Parsed {len(results['hosts'])} host(s)")
        
        if results['hosts']:
            host = results['hosts'][0]
            print(f"Host IP: {host['ip']}")
            print(f"Hostname: {host['hostname']}")
            print(f"Status: {host['status']}")
            print(f"Services found: {len(host['services'])}")
            print(f"Vulnerabilities found: {len(host['vulnerabilities'])}")
            
            for service in host['services']:
                print(f"  Port {service['port']}/{service['protocol']}: {service['service']} ({service['version']})")
                
            for vuln in host['vulnerabilities']:
                print(f"  Vulnerability: {vuln['script_id']}")
        
        return True
    except Exception as e:
        print(f"Parser test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running tech-security-audit skill test...")
    success = test_parser_with_sample_data()
    
    if success:
        print("\nSkill framework test PASSED")
        print("The tech-security-audit skill is ready to use once Nmap is properly installed.")
    else:
        print("\nSkill framework test FAILED")