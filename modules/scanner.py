#!/usr/bin/env python3
"""
AutoPentestX - Network Scanner Module
Handles port scanning, OS detection, and service enumeration using Nmap
"""

import nmap
import subprocess
import json
import re
from datetime import datetime

class Scanner:
    def __init__(self, target):
        """Initialize scanner with target"""
        self.target = target
        self.nm = nmap.PortScanner()
        self.scan_results = {
            'target': target,
            'os_detection': 'Unknown',
            'ports': [],
            'services': [],
            'scan_time': None
        }
    
    def validate_target(self):
        """Validate target IP or domain"""
        try:
            # Try to resolve the target
            import socket
            socket.gethostbyname(self.target)
            return True
        except socket.gaierror:
            print(f"[✗] Invalid target: {self.target}")
            return False
    
    def detect_os(self):
        """Detect operating system using Nmap"""
        print(f"[*] Detecting operating system for {self.target}...")
        try:
            # Run OS detection with Nmap (requires root/sudo)
            self.nm.scan(self.target, arguments='-O -Pn')
            
            if self.target in self.nm.all_hosts():
                if 'osmatch' in self.nm[self.target]:
                    os_matches = self.nm[self.target]['osmatch']
                    if os_matches:
                        os_name = os_matches[0]['name']
                        accuracy = os_matches[0]['accuracy']
                        self.scan_results['os_detection'] = f"{os_name} (Accuracy: {accuracy}%)"
                        print(f"[✓] OS Detected: {os_name} ({accuracy}% accuracy)")
                        return self.scan_results['os_detection']
            
            # Fallback: Try using TTL values
            result = subprocess.run(['ping', '-c', '1', self.target], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                ttl_match = re.search(r'ttl=(\d+)', result.stdout.lower())
                if ttl_match:
                    ttl = int(ttl_match.group(1))
                    if ttl <= 64:
                        self.scan_results['os_detection'] = "Linux/Unix (TTL <= 64)"
                    elif ttl <= 128:
                        self.scan_results['os_detection'] = "Windows (TTL <= 128)"
                    else:
                        self.scan_results['os_detection'] = "Unknown (TTL > 128)"
                    
                    print(f"[✓] OS Detected (TTL-based): {self.scan_results['os_detection']}")
                    return self.scan_results['os_detection']
            
            self.scan_results['os_detection'] = "Unknown"
            print("[!] Could not detect OS reliably")
            return "Unknown"
            
        except Exception as e:
            print(f"[!] OS Detection failed: {e}")
            self.scan_results['os_detection'] = "Unknown"
            return "Unknown"
    
    def scan_all_ports(self):
        """Perform comprehensive port scan"""
        print(f"[*] Scanning all TCP ports on {self.target}...")
        try:
            start_time = datetime.now()
            
            # Scan top 1000 ports first (faster)
            print("[*] Phase 1: Scanning top 1000 ports...")
            self.nm.scan(self.target, arguments='-sS -sV -T4 -Pn --top-ports 1000')
            
            if self.target in self.nm.all_hosts():
                host = self.nm[self.target]
                
                # Process TCP ports
                if 'tcp' in host:
                    for port in host['tcp'].keys():
                        port_info = host['tcp'][port]
                        if port_info['state'] == 'open':
                            port_data = {
                                'port': port,
                                'protocol': 'tcp',
                                'state': port_info['state'],
                                'service': port_info.get('name', 'unknown'),
                                'version': port_info.get('product', '') + ' ' + port_info.get('version', ''),
                                'extrainfo': port_info.get('extrainfo', '')
                            }
                            self.scan_results['ports'].append(port_data)
                            print(f"[✓] Port {port}/tcp open - {port_data['service']} {port_data['version']}")
                
                # Process UDP ports (limited scan for speed)
                print("[*] Phase 2: Scanning common UDP ports...")
                self.nm.scan(self.target, arguments='-sU -Pn --top-ports 20')
                
                if 'udp' in self.nm[self.target]:
                    for port in self.nm[self.target]['udp'].keys():
                        port_info = self.nm[self.target]['udp'][port]
                        if port_info['state'] in ['open', 'open|filtered']:
                            port_data = {
                                'port': port,
                                'protocol': 'udp',
                                'state': port_info['state'],
                                'service': port_info.get('name', 'unknown'),
                                'version': port_info.get('product', '') + ' ' + port_info.get('version', ''),
                                'extrainfo': port_info.get('extrainfo', '')
                            }
                            self.scan_results['ports'].append(port_data)
                            print(f"[✓] Port {port}/udp {port_info['state']} - {port_data['service']}")
            
            end_time = datetime.now()
            scan_duration = (end_time - start_time).total_seconds()
            self.scan_results['scan_time'] = scan_duration
            
            print(f"[✓] Port scan completed in {scan_duration:.2f} seconds")
            print(f"[✓] Total open ports found: {len(self.scan_results['ports'])}")
            
            return self.scan_results['ports']
            
        except Exception as e:
            print(f"[✗] Port scanning failed: {e}")
            return []
    
    def enumerate_services(self):
        """Extract detailed service information"""
        print(f"[*] Enumerating services on {self.target}...")
        
        services = []
        for port_data in self.scan_results['ports']:
            service_info = {
                'port': port_data['port'],
                'protocol': port_data['protocol'],
                'service': port_data['service'],
                'version': port_data['version'].strip(),
                'banner': port_data.get('extrainfo', ''),
                'vulnerabilities': []
            }
            services.append(service_info)
        
        self.scan_results['services'] = services
        print(f"[✓] Enumerated {len(services)} services")
        return services
    
    def run_full_scan(self):
        """Execute complete scan workflow"""
        print("\n" + "="*60)
        print("AutoPentestX - Network Scanner")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"Scan started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Validate target
        if not self.validate_target():
            return None
        
        # Step 1: OS Detection
        self.detect_os()
        
        # Step 2: Port Scanning
        self.scan_all_ports()
        
        # Step 3: Service Enumeration
        self.enumerate_services()
        
        print("\n" + "="*60)
        print("SCAN SUMMARY")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"OS: {self.scan_results['os_detection']}")
        print(f"Open Ports: {len(self.scan_results['ports'])}")
        print(f"Services Detected: {len(self.scan_results['services'])}")
        print("="*60 + "\n")
        
        return self.scan_results
    
    def get_results(self):
        """Return scan results"""
        return self.scan_results
    
    def save_results(self, filename):
        """Save scan results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.scan_results, f, indent=4)
            print(f"[✓] Scan results saved to {filename}")
        except Exception as e:
            print(f"[✗] Failed to save results: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    scanner = Scanner(target)
    results = scanner.run_full_scan()
    
    if results:
        scanner.save_results(f"scan_{target.replace('.', '_')}.json")
