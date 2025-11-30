#!/usr/bin/env python3
"""
AutoPentestX - PDF Report Generator
Generates professional penetration testing reports using ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class PDFReportGenerator:
    def __init__(self, target, scan_id):
        """Initialize PDF report generator"""
        self.target = target
        self.scan_id = scan_id
        self.timestamp = datetime.now()
        self.filename = f"reports/AutoPentestX_Report_{target.replace('.', '_')}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        # Initialize document
        self.doc = SimpleDocTemplate(self.filename, pagesize=letter)
        self.story = []
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.create_custom_styles()
    
    def create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='CriticalRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.orangered,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.blue,
            fontName='Helvetica-Bold'
        ))
    
    def add_cover_page(self, tester_name="AutoPentestX Team"):
        """Add cover page to report"""
        # Title
        title = Paragraph("PENETRATION TESTING REPORT", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Target information
        target_info = f"""
        <para align=center fontSize=14>
        <b>Target System:</b> {self.target}<br/>
        <b>Scan ID:</b> {self.scan_id}<br/>
        <b>Report Date:</b> {self.timestamp.strftime('%B %d, %Y')}<br/>
        <b>Report Time:</b> {self.timestamp.strftime('%H:%M:%S %Z')}<br/>
        </para>
        """
        self.story.append(Paragraph(target_info, self.styles['Normal']))
        self.story.append(Spacer(1, 1*inch))
        
        # Confidential notice
        confidential = """
        <para align=center fontSize=12 textColor=red>
        <b>CONFIDENTIAL</b><br/>
        This report contains sensitive security information.<br/>
        Handle with appropriate care and restrict distribution.
        </para>
        """
        self.story.append(Paragraph(confidential, self.styles['Normal']))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Tester information
        tester_info = f"""
        <para align=center fontSize=12>
        <b>Prepared by:</b> {tester_name}<br/>
        <b>Tool:</b> AutoPentestX v1.0<br/>
        <b>Framework:</b> Automated Penetration Testing Toolkit
        </para>
        """
        self.story.append(Paragraph(tester_info, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, risk_summary):
        """Add executive summary section"""
        self.story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeading']))
        
        overall_risk = risk_summary.get('overall_risk_level', 'UNKNOWN')
        total_vulns = risk_summary.get('total_vulnerabilities', 0)
        
        summary_text = f"""
        <para align=justify>
        This penetration testing report presents the findings of an automated security assessment 
        conducted on the target system <b>{self.target}</b>. The assessment was performed on 
        {self.timestamp.strftime('%B %d, %Y')} using the AutoPentestX automated penetration testing toolkit.
        <br/><br/>
        <b>Overall Risk Level: </b><font color="{self.get_risk_color(overall_risk)}">{overall_risk}</font><br/>
        <b>Total Vulnerabilities Identified: </b>{total_vulns}<br/>
        <b>Critical/High Risk Items: </b>{len(risk_summary.get('high_risk_items', []))}<br/>
        <b>Web Vulnerabilities: </b>{risk_summary.get('web_vulnerabilities', 0)}<br/>
        <b>SQL Injection Points: </b>{risk_summary.get('sql_vulnerabilities', 0)}<br/>
        </para>
        """
        
        self.story.append(Paragraph(summary_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))
        
        # Risk assessment summary
        if overall_risk in ['CRITICAL', 'HIGH']:
            warning = f"""
            <para align=justify textColor=red>
            <b>⚠ CRITICAL FINDING:</b> The target system exhibits {overall_risk} risk level. 
            Immediate remediation action is required to address identified security vulnerabilities 
            before the system can be considered secure for production use.
            </para>
            """
            self.story.append(Paragraph(warning, self.styles['Normal']))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_scan_details(self, scan_data):
        """Add scan details section"""
        self.story.append(Paragraph("SCAN DETAILS", self.styles['SectionHeading']))
        
        os_detection = scan_data.get('os_detection', 'Unknown')
        scan_time = scan_data.get('scan_time', 0) or 0
        total_ports = len(scan_data.get('ports', []))
        
        details_text = f"""
        <para>
        <b>Target:</b> {self.target}<br/>
        <b>Operating System:</b> {os_detection}<br/>
        <b>Scan Duration:</b> {scan_time:.2f} seconds<br/>
        <b>Total Open Ports:</b> {total_ports}<br/>
        <b>Scan Method:</b> Automated comprehensive scan using Nmap, Nikto, and SQLMap<br/>
        </para>
        """
        
        self.story.append(Paragraph(details_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_open_ports_table(self, ports_data):
        """Add table of open ports"""
        self.story.append(Paragraph("OPEN PORTS AND SERVICES", self.styles['SectionHeading']))
        
        if not ports_data:
            self.story.append(Paragraph("No open ports detected.", self.styles['Normal']))
            return
        
        # Create table data
        table_data = [['Port', 'Protocol', 'State', 'Service', 'Version']]
        
        for port in ports_data[:20]:  # Limit to 20 ports for readability
            table_data.append([
                str(port.get('port', '')),
                port.get('protocol', 'tcp'),
                port.get('state', 'open'),
                port.get('service', 'unknown'),
                port.get('version', 'unknown')[:30]  # Truncate long versions
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_vulnerabilities_table(self, vulnerabilities, cves):
        """Add vulnerabilities table"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("VULNERABILITIES IDENTIFIED", self.styles['SectionHeading']))
        
        all_vulns = []
        
        # Add regular vulnerabilities
        for vuln in vulnerabilities:
            all_vulns.append({
                'port': vuln.get('port', 'N/A'),
                'name': vuln.get('name', 'Unknown'),
                'severity': vuln.get('severity', 'UNKNOWN'),
                'cve_id': vuln.get('cve_id', 'N/A'),
                'description': vuln.get('description', '')[:100]
            })
        
        # Add CVEs
        for cve in cves[:15]:  # Limit CVEs
            all_vulns.append({
                'port': cve.get('port', 'N/A'),
                'name': cve.get('cve_id', 'Unknown'),
                'severity': cve.get('risk_level', 'UNKNOWN'),
                'cve_id': cve.get('cve_id', 'N/A'),
                'description': cve.get('description', '')[:100]
            })
        
        if not all_vulns:
            self.story.append(Paragraph("No vulnerabilities detected.", self.styles['Normal']))
            return
        
        # Create table
        table_data = [['Port', 'Vulnerability', 'Severity', 'CVE ID']]
        
        for vuln in all_vulns[:25]:  # Limit to 25 for space
            table_data.append([
                str(vuln['port']),
                vuln['name'][:40],
                vuln['severity'],
                vuln['cve_id']
            ])
        
        table = Table(table_data, colWidths=[0.7*inch, 2.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_risk_assessment(self, risk_summary):
        """Add risk assessment section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("RISK ASSESSMENT", self.styles['SectionHeading']))
        
        overall_risk = risk_summary.get('overall_risk_level', 'UNKNOWN')
        total_risk_score = risk_summary.get('total_risk_score', 0)
        
        risk_text = f"""
        <para align=justify>
        Based on the comprehensive analysis of identified vulnerabilities, their severity levels, 
        exploitability, and potential impact, the overall risk assessment for the target system is:
        <br/><br/>
        <b>Overall Risk Level:</b> <font color="{self.get_risk_color(overall_risk)}">{overall_risk}</font><br/>
        <b>Total Risk Score:</b> {total_risk_score:.2f}<br/>
        <b>Average Risk per Port:</b> {risk_summary.get('average_risk_per_port', 0):.2f}<br/>
        </para>
        """
        
        self.story.append(Paragraph(risk_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # High risk items
        high_risk_items = risk_summary.get('high_risk_items', [])
        if high_risk_items:
            self.story.append(Paragraph("<b>High Risk Items:</b>", self.styles['Normal']))
            
            for item in high_risk_items[:10]:
                if isinstance(item, dict):
                    if 'port' in item:
                        item_text = f"• Port {item.get('port')}: {item.get('service', 'Unknown')} - Risk Score: {item.get('risk_score', 0)}/10"
                    else:
                        item_text = f"• {item.get('category', 'Unknown')}: {item.get('count', 0)} issues found"
                    
                    self.story.append(Paragraph(item_text, self.styles['Normal']))
            
            self.story.append(Spacer(1, 0.2*inch))
    
    def add_exploitation_results(self, exploit_results):
        """Add exploitation results section"""
        self.story.append(Paragraph("EXPLOITATION ASSESSMENT", self.styles['SectionHeading']))
        
        if not exploit_results:
            self.story.append(Paragraph("No exploitation attempts were made.", self.styles['Normal']))
            return
        
        exploit_text = f"""
        <para align=justify>
        The following exploitation scenarios were evaluated in SAFE MODE. 
        No actual exploitation was performed to prevent system damage.
        <br/><br/>
        <b>Total Exploits Identified:</b> {len(exploit_results)}<br/>
        </para>
        """
        
        self.story.append(Paragraph(exploit_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # List exploits
        for exploit in exploit_results[:10]:
            exploit_info = f"""
            <para>
            <b>• Port {exploit.get('port')}:</b> {exploit.get('exploit_name', 'Unknown')}<br/>
            &nbsp;&nbsp;<i>Status:</i> {exploit.get('status', 'Unknown')}<br/>
            &nbsp;&nbsp;<i>Description:</i> {exploit.get('description', 'N/A')[:100]}<br/>
            </para>
            """
            self.story.append(Paragraph(exploit_info, self.styles['Normal']))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_recommendations(self, recommendations):
        """Add security recommendations"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("SECURITY RECOMMENDATIONS", self.styles['SectionHeading']))
        
        if not recommendations:
            self.story.append(Paragraph("No specific recommendations available.", self.styles['Normal']))
            return
        
        intro = """
        <para align=justify>
        Based on the identified vulnerabilities and risk assessment, the following remediation 
        actions are recommended to improve the security posture of the target system:
        </para>
        """
        self.story.append(Paragraph(intro, self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Group by priority
        priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        for priority in priorities:
            priority_recs = [r for r in recommendations if r.get('priority') == priority]
            
            if priority_recs:
                self.story.append(Paragraph(f"<b>{priority} Priority:</b>", self.styles['Normal']))
                
                for rec in priority_recs[:5]:
                    rec_text = f"""
                    <para>
                    <b>• {rec.get('action', 'Unknown Action')}</b><br/>
                    &nbsp;&nbsp;{rec.get('description', 'No description')}<br/>
                    </para>
                    """
                    self.story.append(Paragraph(rec_text, self.styles['Normal']))
                
                self.story.append(Spacer(1, 0.15*inch))
    
    def add_conclusion(self):
        """Add conclusion section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("CONCLUSION", self.styles['SectionHeading']))
        
        conclusion_text = """
        <para align=justify>
        This automated penetration testing assessment has identified various security vulnerabilities 
        and potential risks in the target system. The findings should be carefully reviewed and 
        prioritized based on the risk levels assigned.
        <br/><br/>
        It is strongly recommended to address all CRITICAL and HIGH severity findings immediately, 
        followed by MEDIUM and LOW severity items according to available resources and priorities.
        <br/><br/>
        Regular security assessments should be conducted to maintain a strong security posture 
        and protect against emerging threats.
        <br/><br/>
        <b>Important Notes:</b><br/>
        • This assessment was conducted using automated tools and may not identify all vulnerabilities<br/>
        • Manual verification and testing is recommended for critical systems<br/>
        • Results should be validated before taking remediation actions<br/>
        • This report is confidential and should be handled securely<br/>
        </para>
        """
        
        self.story.append(Paragraph(conclusion_text, self.styles['Normal']))
    
    def add_disclaimer(self):
        """Add legal disclaimer"""
        self.story.append(Spacer(1, 0.5*inch))
        
        disclaimer_text = """
        <para align=justify fontSize=9 textColor=grey>
        <b>DISCLAIMER:</b> This penetration testing report is provided for educational and authorized 
        security assessment purposes only. The tools and techniques used are intended for legitimate 
        security testing in controlled environments with proper authorization. Unauthorized use of 
        these tools against systems you do not own or have explicit permission to test is illegal 
        and unethical. The developers and users of AutoPentestX assume no liability for misuse or 
        damage caused by this tool.
        </para>
        """
        
        self.story.append(Paragraph(disclaimer_text, self.styles['Normal']))
    
    def get_risk_color(self, risk_level):
        """Get color code for risk level"""
        colors_map = {
            'CRITICAL': 'red',
            'HIGH': 'orangered',
            'MEDIUM': 'orange',
            'LOW': 'blue',
            'MINIMAL': 'green',
            'UNKNOWN': 'grey'
        }
        return colors_map.get(risk_level, 'black')
    
    def generate_report(self, scan_data, vulnerabilities, cves, web_vulns, sql_vulns, 
                       risk_summary, exploit_results, tester_name="AutoPentestX Team"):
        """Generate complete PDF report"""
        print("\n" + "="*60)
        print("AutoPentestX - PDF Report Generation")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"Generating report: {self.filename}")
        print("="*60 + "\n")
        
        try:
            # Build report sections
            print("[*] Adding cover page...")
            self.add_cover_page(tester_name)
            
            print("[*] Adding executive summary...")
            self.add_executive_summary(risk_summary)
            
            print("[*] Adding scan details...")
            self.add_scan_details(scan_data)
            
            print("[*] Adding open ports table...")
            self.add_open_ports_table(scan_data.get('ports', []))
            
            print("[*] Adding vulnerabilities...")
            self.add_vulnerabilities_table(vulnerabilities, cves)
            
            print("[*] Adding risk assessment...")
            self.add_risk_assessment(risk_summary)
            
            print("[*] Adding exploitation results...")
            self.add_exploitation_results(exploit_results)
            
            print("[*] Adding recommendations...")
            self.add_recommendations(risk_summary.get('recommendations', []))
            
            print("[*] Adding conclusion...")
            self.add_conclusion()
            
            print("[*] Adding disclaimer...")
            self.add_disclaimer()
            
            # Build PDF
            print("[*] Building PDF document...")
            self.doc.build(self.story)
            
            print("\n" + "="*60)
            print("PDF REPORT GENERATED SUCCESSFULLY")
            print("="*60)
            print(f"Report saved to: {self.filename}")
            print(f"File size: {os.path.getsize(self.filename) / 1024:.2f} KB")
            print("="*60 + "\n")
            
            return self.filename
            
        except Exception as e:
            print(f"[✗] Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    # Test PDF generator
    print("Testing PDF Report Generator...")
    
    sample_scan = {
        'target': '192.168.1.100',
        'os_detection': 'Linux Ubuntu 20.04',
        'scan_time': 45.67,
        'ports': [
            {'port': 22, 'protocol': 'tcp', 'state': 'open', 'service': 'ssh', 'version': 'OpenSSH 8.2'},
            {'port': 80, 'protocol': 'tcp', 'state': 'open', 'service': 'http', 'version': 'Apache 2.4.41'}
        ]
    }
    
    sample_vulns = [
        {'port': 22, 'name': 'Outdated SSH', 'severity': 'MEDIUM', 'cve_id': 'N/A', 'description': 'SSH version is outdated'}
    ]
    
    sample_risk = {
        'overall_risk_level': 'MEDIUM',
        'total_risk_score': 15.5,
        'average_risk_per_port': 7.75,
        'high_risk_items': [],
        'total_vulnerabilities': 1,
        'web_vulnerabilities': 0,
        'sql_vulnerabilities': 0,
        'recommendations': [
            {'priority': 'HIGH', 'action': 'Update SSH', 'description': 'Update to latest version'}
        ]
    }
    
    generator = PDFReportGenerator('192.168.1.100', 1)
    generator.generate_report(sample_scan, sample_vulns, [], [], [], sample_risk, [])
