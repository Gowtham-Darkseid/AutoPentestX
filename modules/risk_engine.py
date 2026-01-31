#!/usr/bin/env python3
"""
AutoPentestX - Risk Assessment Engine
Calculates overall risk scores based on vulnerabilities and CVSS scores
"""

from collections import defaultdict
import json

class RiskEngine:
    def __init__(self):
        """Initialize risk engine"""
        self.risk_scores = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 2,
            'UNKNOWN': 1
        }
        
        self.severity_weights = {
            'exploitable': 2.0,
            'public_exploit': 1.5,
            'network_accessible': 1.3,
            'authenticated': 0.7
        }
    
    def calculate_cvss_risk(self, cvss_score):
        """Convert CVSS score to risk level"""
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
    
    def calculate_port_risk(self, port_data, vulnerabilities, cves):
        """Calculate risk for a specific port"""
        risk_score = 0
        risk_factors = []
        
        port_num = port_data.get('port')
        service = port_data.get('service', '').lower()
        
        # Base risk for port exposure
        if port_num < 1024:  # Well-known ports
            risk_score += 1
            risk_factors.append("Well-known port exposed")
        
        # Check for sensitive services
        sensitive_services = ['ftp', 'telnet', 'smtp', 'mysql', 'postgresql', 
                             'microsoft-ds', 'netbios-ssn', 'rdp']
        
        if any(svc in service for svc in sensitive_services):
            risk_score += 2
            risk_factors.append(f"Sensitive service exposed: {service}")
        
        # Check vulnerabilities for this port
        port_vulns = [v for v in vulnerabilities if v.get('port') == port_num]
        
        for vuln in port_vulns:
            severity = vuln.get('severity', 'UNKNOWN')
            risk_score += self.risk_scores.get(severity, 1)
            risk_factors.append(f"{severity} vulnerability: {vuln.get('name', 'Unknown')}")
            
            if vuln.get('exploitable', False):
                risk_score *= 1.5
                risk_factors.append("Exploitable vulnerability detected")
        
        # Check CVEs for this port
        port_cves = [c for c in cves if c.get('port') == port_num]
        
        for cve in port_cves:
            cvss = cve.get('cvss_score', 0)
            risk_score += cvss / 2  # Weight CVE score
            
            if cve.get('exploitable', False):
                risk_score *= 1.3
                risk_factors.append(f"CVE with public exploit: {cve.get('cve_id')}")
        
        # Normalize to 0-10 scale
        normalized_score = min(risk_score, 10.0)
        
        return {
            'port': port_num,
            'service': service,
            'risk_score': round(normalized_score, 2),
            'risk_level': self.calculate_cvss_risk(normalized_score),
            'risk_factors': risk_factors
        }
    
    def calculate_overall_risk(self, scan_data, vulnerabilities, cves, web_vulns, sql_vulns):
        """Calculate overall system risk score"""
        print("\n" + "="*60)
        print("AutoPentestX - Risk Assessment")
        print("="*60)
        
        total_risk = 0
        high_risk_items = []
        port_risks = []
        
        # Analyze each port
        ports = scan_data.get('ports', [])
        
        for port in ports:
            port_risk = self.calculate_port_risk(port, vulnerabilities, cves)
            port_risks.append(port_risk)
            total_risk += port_risk['risk_score']
            
            if port_risk['risk_level'] in ['CRITICAL', 'HIGH']:
                high_risk_items.append(port_risk)
                print(f"[!] HIGH RISK: Port {port_risk['port']} - {port_risk['service']} "
                      f"(Score: {port_risk['risk_score']}/10)")
        
        # Add web vulnerabilities to risk
        web_risk = len(web_vulns) * 2  # Each web vuln adds 2 points
        total_risk += web_risk
        
        if web_vulns:
            print(f"[!] Web vulnerabilities detected: {len(web_vulns)} issues")
            high_risk_items.append({
                'category': 'Web Security',
                'risk_score': web_risk,
                'count': len(web_vulns)
            })
        
        # Add SQL injection vulnerabilities (highest risk)
        sql_risk = len(sql_vulns) * 5  # SQL injection is critical
        total_risk += sql_risk
        
        if sql_vulns:
            print(f"[!] CRITICAL: SQL Injection vulnerabilities found: {len(sql_vulns)}")
            high_risk_items.append({
                'category': 'SQL Injection',
                'risk_score': sql_risk,
                'count': len(sql_vulns),
                'risk_level': 'CRITICAL'
            })
        
        # Calculate average risk per port
        avg_risk = total_risk / len(ports) if ports else 0
        
        # Determine overall risk level
        overall_risk_level = self.determine_overall_risk_level(
            total_risk, avg_risk, high_risk_items
        )
        
        # Risk summary
        risk_summary = {
            'total_risk_score': round(total_risk, 2),
            'average_risk_per_port': round(avg_risk, 2),
            'overall_risk_level': overall_risk_level,
            'high_risk_items': high_risk_items,
            'port_risks': port_risks,
            'total_vulnerabilities': len(vulnerabilities) + len(cves),
            'web_vulnerabilities': len(web_vulns),
            'sql_vulnerabilities': len(sql_vulns),
            'recommendations': self.generate_recommendations(
                overall_risk_level, high_risk_items, vulnerabilities, cves
            )
        }
        
        # Print summary
        print("\n" + "="*60)
        print("RISK ASSESSMENT SUMMARY")
        print("="*60)
        print(f"Overall Risk Level: {overall_risk_level}")
        print(f"Total Risk Score: {risk_summary['total_risk_score']}")
        print(f"Average Risk per Port: {risk_summary['average_risk_per_port']}")
        print(f"High Risk Items: {len(high_risk_items)}")
        print(f"Total Vulnerabilities: {risk_summary['total_vulnerabilities']}")
        print("="*60 + "\n")
        
        return risk_summary
    
    def determine_overall_risk_level(self, total_risk, avg_risk, high_risk_items):
        """Determine overall system risk level"""
        # Count critical and high risk items
        critical_count = len([item for item in high_risk_items 
                             if item.get('risk_level') == 'CRITICAL'])
        high_count = len([item for item in high_risk_items 
                         if item.get('risk_level') == 'HIGH'])
        
        # Decision logic
        if critical_count > 0 or total_risk > 50:
            return "CRITICAL"
        elif high_count >= 3 or total_risk > 30:
            return "HIGH"
        elif avg_risk > 4 or total_risk > 15:
            return "MEDIUM"
        elif total_risk > 5:
            return "LOW"
        else:
            return "MINIMAL"
    
    def generate_recommendations(self, risk_level, high_risk_items, vulnerabilities, cves):
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # General recommendations by risk level
        if risk_level in ['CRITICAL', 'HIGH']:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediate Action Required',
                'description': 'Critical vulnerabilities detected. Isolate system and patch immediately.'
            })
        
        # Specific recommendations based on vulnerabilities
        vuln_types = defaultdict(int)
        for vuln in vulnerabilities:
            vuln_types[vuln.get('service', 'unknown')] += 1
        
        for service, count in vuln_types.items():
            if count > 0:
                recommendations.append({
                    'priority': 'HIGH',
                    'action': f'Update {service} service',
                    'description': f'Found {count} vulnerabilities in {service}. Update to latest version.'
                })
        
        # CVE-based recommendations
        critical_cves = [cve for cve in cves if cve.get('risk_level') == 'CRITICAL']
        if critical_cves:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Patch Critical CVEs',
                'description': f'Apply security patches for {len(critical_cves)} critical CVEs.'
            })
        
        # SQL Injection recommendations
        if any('sql' in str(item).lower() for item in high_risk_items):
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Fix SQL Injection Vulnerabilities',
                'description': 'Implement parameterized queries and input validation immediately.'
            })
        
        # General security recommendations
        recommendations.extend([
            {
                'priority': 'MEDIUM',
                'action': 'Enable Firewall',
                'description': 'Configure firewall to restrict access to necessary ports only.'
            },
            {
                'priority': 'MEDIUM',
                'action': 'Update All Services',
                'description': 'Ensure all services are running latest stable versions.'
            },
            {
                'priority': 'LOW',
                'action': 'Implement Monitoring',
                'description': 'Set up intrusion detection and continuous monitoring.'
            },
            {
                'priority': 'LOW',
                'action': 'Security Hardening',
                'description': 'Apply security hardening guidelines for the operating system.'
            }
        ])
        
        return recommendations
    
    def save_risk_assessment(self, risk_summary, filename):
        """Save risk assessment to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(risk_summary, f, indent=4)
            print(f"[✓] Risk assessment saved to {filename}")
        except Exception as e:
            print(f"[✗] Failed to save risk assessment: {e}")


if __name__ == "__main__":
    # Test risk engine
    risk_engine = RiskEngine()
    
    sample_scan = {
        'ports': [
            {'port': 22, 'service': 'ssh'},
            {'port': 80, 'service': 'http'},
            {'port': 3306, 'service': 'mysql'}
        ]
    }
    
    sample_vulns = [
        {'port': 22, 'name': 'Outdated SSH', 'severity': 'MEDIUM', 'exploitable': False},
        {'port': 3306, 'name': 'MySQL Exposed', 'severity': 'HIGH', 'exploitable': True}
    ]
    
    sample_cves = [
        {'port': 22, 'cve_id': 'CVE-2021-1234', 'cvss_score': 7.5, 'exploitable': False}
    ]
    
    results = risk_engine.calculate_overall_risk(sample_scan, sample_vulns, sample_cves, [], [])
    print(json.dumps(results, indent=2))
