#!/usr/bin/env python3
"""
AutoPentestX - Vulnerability Scanner Module
Integrates Nikto (web scanning) and SQLMap (SQL injection detection)
"""

import subprocess
import json
import re
import os
from datetime import datetime

class VulnerabilityScanner:
    def __init__(self, target, ports_data):
        """Initialize vulnerability scanner"""
        self.target = target
        self.ports_data = ports_data
        self.web_ports = []
        self.vulnerabilities = []
        self.web_vulns = []
        self.sql_vulns = []
        
        # Identify web ports
        self.identify_web_services()
    
    def identify_web_services(self):
        """Identify HTTP/HTTPS services from port scan"""
        common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000]
        web_services = ['http', 'https', 'ssl/http', 'http-proxy', 'http-alt']
        
        for port in self.ports_data:
            service = port.get('service', '').lower()
            port_num = port.get('port')
            
            # Check if it's a known web service or common web port
            if any(web_svc in service for web_svc in web_services) or port_num in common_web_ports:
                protocol = 'https' if port_num == 443 or 'https' in service or 'ssl' in service else 'http'
                self.web_ports.append({
                    'port': port_num,
                    'protocol': protocol,
                    'url': f"{protocol}://{self.target}:{port_num}"
                })
                print(f"[✓] Detected web service: {protocol}://{self.target}:{port_num}")
    
    def scan_with_nikto(self, url):
        """Run Nikto web vulnerability scanner"""
        print(f"[*] Running Nikto scan on {url}...")
        
        try:
            # Check if Nikto is installed
            nikto_check = subprocess.run(['which', 'nikto'], capture_output=True)
            if nikto_check.returncode != 0:
                print("[!] Nikto not installed, skipping web vulnerability scan")
                return []
            
            # Run Nikto
            cmd = [
                'nikto',
                '-h', url,
                '-Format', 'json',
                '-output', f'logs/nikto_{self.target}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                '-Tuning', '123456789',  # All tests
                '-timeout', '10'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse Nikto output
            vulns = self.parse_nikto_output(result.stdout)
            
            print(f"[✓] Nikto scan completed: {len(vulns)} vulnerabilities found")
            return vulns
            
        except subprocess.TimeoutExpired:
            print("[!] Nikto scan timed out")
            return []
        except Exception as e:
            print(f"[!] Nikto scan failed: {e}")
            return []
    
    def parse_nikto_output(self, output):
        """Parse Nikto JSON output"""
        vulnerabilities = []
        
        try:
            # Try to parse as JSON
            if output:
                # Nikto output may have multiple JSON objects
                json_objects = re.findall(r'\{.*?\}', output, re.DOTALL)
                
                for json_str in json_objects:
                    try:
                        data = json.loads(json_str)
                        if 'vulnerabilities' in data:
                            for vuln in data['vulnerabilities']:
                                vulnerabilities.append({
                                    'type': 'web',
                                    'url': vuln.get('url', ''),
                                    'severity': self.map_nikto_severity(vuln.get('OSVDB', '')),
                                    'description': vuln.get('msg', 'Unknown vulnerability')
                                })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[!] Error parsing Nikto output: {e}")
        
        # If JSON parsing fails, try text parsing
        if not vulnerabilities and output:
            lines = output.split('\n')
            for line in lines:
                if '+ ' in line and any(keyword in line.lower() for keyword in 
                    ['vulnerable', 'outdated', 'disclosure', 'injection', 'xss', 'security']):
                    vulnerabilities.append({
                        'type': 'web',
                        'url': self.target,
                        'severity': 'MEDIUM',
                        'description': line.strip()
                    })
        
        return vulnerabilities
    
    def map_nikto_severity(self, osvdb_id):
        """Map OSVDB ID to severity level"""
        if not osvdb_id:
            return 'MEDIUM'
        # Simplified severity mapping
        return 'MEDIUM'
    
    def scan_sql_injection(self, url):
        """Scan for SQL injection vulnerabilities using SQLMap"""
        print(f"[*] Scanning for SQL injection on {url}...")
        
        try:
            # Check if SQLMap is installed
            sqlmap_check = subprocess.run(['which', 'sqlmap'], capture_output=True)
            if sqlmap_check.returncode != 0:
                print("[!] SQLMap not installed, skipping SQL injection scan")
                return []
            
            # Run SQLMap with batch mode and basic options
            cmd = [
                'sqlmap',
                '-u', url,
                '--batch',
                '--crawl=2',
                '--level=1',
                '--risk=1',
                '--random-agent',
                '--timeout=30',
                '--retries=2',
                '--threads=3'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            # Parse SQLMap output
            sql_vulns = self.parse_sqlmap_output(result.stdout, url)
            
            print(f"[✓] SQL injection scan completed: {len(sql_vulns)} vulnerabilities found")
            return sql_vulns
            
        except subprocess.TimeoutExpired:
            print("[!] SQLMap scan timed out")
            return []
        except Exception as e:
            print(f"[!] SQLMap scan failed: {e}")
            return []
    
    def parse_sqlmap_output(self, output, url):
        """Parse SQLMap output for vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Look for SQL injection indicators
            if 'parameter' in output.lower() and 'injectable' in output.lower():
                # Extract injectable parameters
                param_matches = re.findall(r"Parameter: (.*?) \(.*?\) is vulnerable", output, re.IGNORECASE)
                
                for param in param_matches:
                    vulnerabilities.append({
                        'type': 'sql_injection',
                        'url': url,
                        'parameter': param,
                        'severity': 'HIGH',
                        'description': f"SQL Injection vulnerability found in parameter: {param}"
                    })
            
            # Check for database information
            if 'back-end DBMS' in output:
                db_match = re.search(r'back-end DBMS: (.*?)[\n\r]', output)
                if db_match and vulnerabilities:
                    vulnerabilities[0]['database'] = db_match.group(1)
        
        except Exception as e:
            print(f"[!] Error parsing SQLMap output: {e}")
        
        return vulnerabilities
    
    def scan_common_vulnerabilities(self):
        """Scan for common vulnerabilities based on service versions"""
        print("[*] Checking for common vulnerabilities based on service versions...")
        
        common_vulns = []
        
        for port in self.ports_data:
            service = port.get('service', '').lower()
            version = port.get('version', '').lower()
            port_num = port.get('port')
            
            # Check for outdated/vulnerable services
            vuln_checks = [
                # SSH vulnerabilities
                {
                    'service': 'ssh',
                    'versions': ['openssh 5', 'openssh 6', 'openssh 7.0', 'openssh 7.1', 'openssh 7.2'],
                    'vuln_name': 'Outdated SSH Version',
                    'description': 'SSH service running outdated version with known vulnerabilities',
                    'severity': 'MEDIUM'
                },
                # FTP vulnerabilities
                {
                    'service': 'ftp',
                    'versions': ['vsftpd 2.3.4', 'proftpd 1.3.3'],
                    'vuln_name': 'Vulnerable FTP Service',
                    'description': 'FTP service with known backdoor or vulnerabilities',
                    'severity': 'HIGH'
                },
                # SMB vulnerabilities
                {
                    'service': 'microsoft-ds',
                    'versions': ['smb'],
                    'vuln_name': 'SMB Service Exposed',
                    'description': 'SMB service exposed, potential for EternalBlue or similar exploits',
                    'severity': 'HIGH'
                },
                # MySQL vulnerabilities
                {
                    'service': 'mysql',
                    'versions': ['5.0', '5.1', '5.5'],
                    'vuln_name': 'Outdated MySQL Version',
                    'description': 'MySQL running outdated version with known vulnerabilities',
                    'severity': 'MEDIUM'
                },
                # Apache vulnerabilities
                {
                    'service': 'http',
                    'versions': ['apache 2.0', 'apache 2.2'],
                    'vuln_name': 'Outdated Apache Server',
                    'description': 'Apache HTTP server running outdated version',
                    'severity': 'MEDIUM'
                }
            ]
            
            # Check each vulnerability pattern
            for check in vuln_checks:
                if check['service'] in service:
                    for vuln_version in check['versions']:
                        if vuln_version in version or version == '':
                            common_vulns.append({
                                'port': port_num,
                                'service': service,
                                'name': check['vuln_name'],
                                'description': check['description'],
                                'severity': check['severity'],
                                'version': version,
                                'exploitable': True
                            })
                            print(f"[!] Found: {check['vuln_name']} on port {port_num}")
                            break
        
        return common_vulns
    
    def run_full_scan(self):
        """Execute complete vulnerability scan"""
        print("\n" + "="*60)
        print("AutoPentestX - Vulnerability Scanner")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"Services to scan: {len(self.ports_data)}")
        print("="*60 + "\n")
        
        # Scan common vulnerabilities
        common_vulns = self.scan_common_vulnerabilities()
        self.vulnerabilities.extend(common_vulns)
        
        # Scan web services if found
        if self.web_ports:
            print(f"\n[*] Found {len(self.web_ports)} web service(s)")
            
            for web_service in self.web_ports:
                url = web_service['url']
                
                # Nikto scan
                nikto_vulns = self.scan_with_nikto(url)
                self.web_vulns.extend(nikto_vulns)
                
                # SQL injection scan
                sql_vulns = self.scan_sql_injection(url)
                self.sql_vulns.extend(sql_vulns)
        
        else:
            print("[!] No web services detected")
        
        print("\n" + "="*60)
        print("VULNERABILITY SCAN SUMMARY")
        print("="*60)
        print(f"Common Vulnerabilities: {len(common_vulns)}")
        print(f"Web Vulnerabilities: {len(self.web_vulns)}")
        print(f"SQL Injection Points: {len(self.sql_vulns)}")
        print(f"Total Vulnerabilities: {len(self.vulnerabilities) + len(self.web_vulns) + len(self.sql_vulns)}")
        print("="*60 + "\n")
        
        return {
            'vulnerabilities': self.vulnerabilities,
            'web_vulnerabilities': self.web_vulns,
            'sql_vulnerabilities': self.sql_vulns
        }
    
    def get_results(self):
        """Return vulnerability scan results"""
        return {
            'vulnerabilities': self.vulnerabilities,
            'web_vulnerabilities': self.web_vulns,
            'sql_vulnerabilities': self.sql_vulns
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vuln_scanner.py <target>")
        sys.exit(1)
    
    # This would normally receive port data from scanner module
    # For testing, we'll use sample data
    target = sys.argv[1]
    sample_ports = [
        {'port': 80, 'service': 'http', 'version': 'Apache 2.2.8'},
        {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 7.0'}
    ]
    
    vuln_scanner = VulnerabilityScanner(target, sample_ports)
    results = vuln_scanner.run_full_scan()
