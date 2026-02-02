#!/usr/bin/env python3
"""
AutoPentestX - CVE Lookup Module
Looks up CVE information for discovered services and versions
"""

import requests
import json
import re
from datetime import datetime
import time

class CVELookup:
    def __init__(self):
        """Initialize CVE lookup module"""
        self.cve_data = []
        self.api_url = "https://cve.circl.lu/api"
        self.nvd_api = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
    def search_cve_by_product(self, product, version=""):
        """Search for CVEs by product name and version"""
        print(f"[*] Searching CVEs for: {product} {version}")
        
        cves = []
        
        try:
            # Clean product name
            product_clean = product.lower().strip()
            product_clean = re.sub(r'[^\w\s-]', '', product_clean)
            
            # Try CVE CIRCL API
            search_url = f"{self.api_url}/search/{product_clean}"
            
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Limit results to most recent/relevant
                    for cve_entry in data[:10]:  # Top 10 results
                        cve_info = self.parse_cve_entry(cve_entry)
                        
                        # Filter by version if specified
                        if version and version.strip():
                            if self.version_matches(cve_entry, version):
                                cves.append(cve_info)
                        else:
                            cves.append(cve_info)
                
                print(f"[✓] Found {len(cves)} relevant CVEs for {product}")
            
            else:
                print(f"[!] CVE API returned status code: {response.status_code}")
            
            # Rate limiting
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"[!] CVE lookup failed for {product}: {e}")
        except Exception as e:
            print(f"[!] Error during CVE lookup: {e}")
        
        return cves
    
    def parse_cve_entry(self, cve_entry):
        """Parse CVE entry and extract relevant information"""
        try:
            cve_id = cve_entry.get('id', 'Unknown')
            summary = cve_entry.get('summary', 'No description available')
            
            # Get CVSS score
            cvss_score = 0.0
            if 'cvss' in cve_entry:
                cvss_score = float(cve_entry.get('cvss', 0.0))
            elif 'impact' in cve_entry:
                if 'baseMetricV3' in cve_entry['impact']:
                    cvss_score = float(cve_entry['impact']['baseMetricV3'].get('cvssV3', {}).get('baseScore', 0.0))
                elif 'baseMetricV2' in cve_entry['impact']:
                    cvss_score = float(cve_entry['impact']['baseMetricV2'].get('cvssV2', {}).get('baseScore', 0.0))
            
            # Determine risk level
            risk_level = self.calculate_risk_level(cvss_score)
            
            # Get published date
            published = cve_entry.get('Published', cve_entry.get('published', 'Unknown'))
            
            # Check if exploit is available
            exploitable = self.check_exploit_availability(cve_id, cve_entry)
            
            return {
                'cve_id': cve_id,
                'description': summary[:500],  # Limit description length
                'cvss_score': cvss_score,
                'risk_level': risk_level,
                'published_date': published,
                'exploitable': exploitable,
                'references': cve_entry.get('references', [])[:3]  # Top 3 references
            }
        
        except Exception as e:
            print(f"[!] Error parsing CVE entry: {e}")
            return {
                'cve_id': 'Unknown',
                'description': 'Error parsing CVE data',
                'cvss_score': 0.0,
                'risk_level': 'UNKNOWN',
                'published_date': 'Unknown',
                'exploitable': False,
                'references': []
            }
    
    def calculate_risk_level(self, cvss_score):
        """Calculate risk level based on CVSS score"""
        if cvss_score >= 9.0:
            return "CRITICAL"
        elif cvss_score >= 7.0:
            return "HIGH"
        elif cvss_score >= 4.0:
            return "MEDIUM"
        elif cvss_score > 0.0:
            return "LOW"
        else:
            return "UNKNOWN"
    
    def check_exploit_availability(self, cve_id, cve_entry):
        """Check if exploit is publicly available"""
        # Check in CVE data
        if 'exploit-db' in str(cve_entry).lower():
            return True
        
        if 'metasploit' in str(cve_entry).lower():
            return True
        
        # Check references
        if 'references' in cve_entry:
            for ref in cve_entry['references']:
                ref_str = str(ref).lower()
                if any(keyword in ref_str for keyword in ['exploit', 'poc', 'metasploit', 'exploit-db']):
                    return True
        
        return False
    
    def version_matches(self, cve_entry, version):
        """Check if CVE applies to specific version"""
        try:
            # Simple version matching - can be enhanced
            cve_text = json.dumps(cve_entry).lower()
            version_clean = version.lower().strip()
            
            # Extract version numbers
            version_nums = re.findall(r'\d+\.\d+', version_clean)
            
            if version_nums:
                for ver in version_nums:
                    if ver in cve_text:
                        return True
            
            # If version is mentioned anywhere in CVE
            if version_clean in cve_text:
                return True
            
            # Default: include if we can't determine
            return True
        
        except:
            return True
    
    def lookup_services(self, services):
        """Lookup CVEs for multiple services"""
        print("\n" + "="*60)
        print("AutoPentestX - CVE Lookup")
        print("="*60)
        print(f"Services to check: {len(services)}")
        print("="*60 + "\n")
        
        all_cves = []
        
        for service in services:
            port = service.get('port')
            service_name = service.get('service', 'unknown')
            version = service.get('version', '')
            
            print(f"\n[*] Checking port {port}: {service_name} {version}")
            
            # Extract product name from service
            product = self.extract_product_name(service_name, version)
            
            if product and product != 'unknown':
                cves = self.search_cve_by_product(product, version)
                
                for cve in cves:
                    cve['port'] = port
                    cve['service'] = service_name
                    cve['version'] = version
                    all_cves.append(cve)
                    
                    print(f"  [!] {cve['cve_id']} - CVSS: {cve['cvss_score']} ({cve['risk_level']})")
        
        self.cve_data = all_cves
        
        print("\n" + "="*60)
        print("CVE LOOKUP SUMMARY")
        print("="*60)
        print(f"Total CVEs found: {len(all_cves)}")
        
        # Count by risk level
        critical = len([c for c in all_cves if c['risk_level'] == 'CRITICAL'])
        high = len([c for c in all_cves if c['risk_level'] == 'HIGH'])
        medium = len([c for c in all_cves if c['risk_level'] == 'MEDIUM'])
        low = len([c for c in all_cves if c['risk_level'] == 'LOW'])
        
        print(f"  CRITICAL: {critical}")
        print(f"  HIGH: {high}")
        print(f"  MEDIUM: {medium}")
        print(f"  LOW: {low}")
        print("="*60 + "\n")
        
        return all_cves
    
    def extract_product_name(self, service_name, version):
        """Extract clean product name for CVE search"""
        # Common product name mappings
        product_map = {
            'http': 'apache',
            'ssh': 'openssh',
            'ftp': 'ftp',
            'smtp': 'postfix',
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'microsoft-ds': 'microsoft windows',
            'netbios-ssn': 'samba',
            'domain': 'bind',
            'ssl/http': 'apache',
            'https': 'apache'
        }
        
        service_lower = service_name.lower()
        
        # Check mapped products
        for key, product in product_map.items():
            if key in service_lower:
                return product
        
        # Try to extract from version string
        version_lower = version.lower()
        
        products = ['apache', 'nginx', 'openssh', 'vsftpd', 'proftpd', 
                   'mysql', 'postgresql', 'bind', 'postfix', 'dovecot']
        
        for product in products:
            if product in version_lower:
                return product
        
        # Return service name if nothing else matches
        return service_name if service_name != 'unknown' else None
    
    def get_results(self):
        """Return CVE lookup results"""
        return self.cve_data
    
    def save_results(self, filename):
        """Save CVE data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.cve_data, f, indent=4)
            print(f"[✓] CVE data saved to {filename}")
        except Exception as e:
            print(f"[✗] Failed to save CVE data: {e}")


if __name__ == "__main__":
    # Test CVE lookup
    cve_lookup = CVELookup()
    
    sample_services = [
        {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 7.4'},
        {'port': 80, 'service': 'http', 'version': 'Apache 2.4.6'}
    ]
    
    results = cve_lookup.lookup_services(sample_services)
    print(f"\nTotal CVEs found: {len(results)}")
