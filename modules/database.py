#!/usr/bin/env python3
"""
AutoPentestX - Database Module
Handles SQLite database operations for storing scan results
"""

import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="database/autopentestx.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.ensure_directory()
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def ensure_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"[✓] Database connected: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[✗] Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create necessary database tables"""
        try:
            # Scans table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    os_detection TEXT,
                    scan_duration REAL,
                    total_ports INTEGER,
                    open_ports INTEGER,
                    vulnerabilities_found INTEGER,
                    risk_score TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # Ports table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    port_number INTEGER,
                    protocol TEXT,
                    state TEXT,
                    service_name TEXT,
                    service_version TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans(id)
                )
            ''')
            
            # Vulnerabilities table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    port_number INTEGER,
                    service_name TEXT,
                    vuln_name TEXT,
                    vuln_description TEXT,
                    cve_id TEXT,
                    cvss_score REAL,
                    risk_level TEXT,
                    exploitable BOOLEAN,
                    FOREIGN KEY (scan_id) REFERENCES scans(id)
                )
            ''')
            
            # Exploits table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS exploits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    vuln_id INTEGER,
                    exploit_name TEXT,
                    exploit_status TEXT,
                    exploit_result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans(id),
                    FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(id)
                )
            ''')
            
            # Web vulnerabilities table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS web_vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    url TEXT,
                    vuln_type TEXT,
                    severity TEXT,
                    description TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans(id)
                )
            ''')
            
            self.conn.commit()
            print("[✓] Database tables created successfully")
            
        except sqlite3.Error as e:
            print(f"[✗] Error creating tables: {e}")
            raise
    
    def insert_scan(self, target, os_detection="Unknown"):
        """Insert new scan record"""
        try:
            self.cursor.execute('''
                INSERT INTO scans (target, os_detection, status)
                VALUES (?, ?, 'in_progress')
            ''', (target, os_detection))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[✗] Error inserting scan: {e}")
            return None
    
    def update_scan(self, scan_id, **kwargs):
        """Update scan record with new information"""
        try:
            updates = []
            values = []
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.append(scan_id)
            query = f"UPDATE scans SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[✗] Error updating scan: {e}")
    
    def insert_port(self, scan_id, port_data):
        """Insert port information"""
        try:
            self.cursor.execute('''
                INSERT INTO ports (scan_id, port_number, protocol, state, service_name, service_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                port_data.get('port'),
                port_data.get('protocol', 'tcp'),
                port_data.get('state', 'open'),
                port_data.get('service', 'unknown'),
                port_data.get('version', 'unknown')
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[✗] Error inserting port: {e}")
    
    def insert_vulnerability(self, scan_id, vuln_data):
        """Insert vulnerability information"""
        try:
            self.cursor.execute('''
                INSERT INTO vulnerabilities 
                (scan_id, port_number, service_name, vuln_name, vuln_description, 
                 cve_id, cvss_score, risk_level, exploitable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                vuln_data.get('port'),
                vuln_data.get('service'),
                vuln_data.get('name'),
                vuln_data.get('description'),
                vuln_data.get('cve_id'),
                vuln_data.get('cvss_score', 0.0),
                vuln_data.get('risk_level', 'UNKNOWN'),
                vuln_data.get('exploitable', False)
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[✗] Error inserting vulnerability: {e}")
            return None
    
    def insert_web_vulnerability(self, scan_id, web_vuln_data):
        """Insert web vulnerability information"""
        try:
            self.cursor.execute('''
                INSERT INTO web_vulnerabilities 
                (scan_id, url, vuln_type, severity, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                scan_id,
                web_vuln_data.get('url'),
                web_vuln_data.get('type'),
                web_vuln_data.get('severity'),
                web_vuln_data.get('description')
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[✗] Error inserting web vulnerability: {e}")
    
    def insert_exploit(self, scan_id, vuln_id, exploit_data):
        """Insert exploit attempt information"""
        try:
            self.cursor.execute('''
                INSERT INTO exploits (scan_id, vuln_id, exploit_name, exploit_status, exploit_result)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                scan_id,
                vuln_id,
                exploit_data.get('name'),
                exploit_data.get('status'),
                exploit_data.get('result')
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[✗] Error inserting exploit: {e}")
    
    def get_scan_data(self, scan_id):
        """Retrieve complete scan data"""
        try:
            # Get scan info
            self.cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
            scan = self.cursor.fetchone()
            
            # Get ports
            self.cursor.execute('SELECT * FROM ports WHERE scan_id = ?', (scan_id,))
            ports = self.cursor.fetchall()
            
            # Get vulnerabilities
            self.cursor.execute('SELECT * FROM vulnerabilities WHERE scan_id = ?', (scan_id,))
            vulnerabilities = self.cursor.fetchall()
            
            # Get web vulnerabilities
            self.cursor.execute('SELECT * FROM web_vulnerabilities WHERE scan_id = ?', (scan_id,))
            web_vulns = self.cursor.fetchall()
            
            # Get exploits
            self.cursor.execute('SELECT * FROM exploits WHERE scan_id = ?', (scan_id,))
            exploits = self.cursor.fetchall()
            
            return {
                'scan': scan,
                'ports': ports,
                'vulnerabilities': vulnerabilities,
                'web_vulnerabilities': web_vulns,
                'exploits': exploits
            }
        except sqlite3.Error as e:
            print(f"[✗] Error retrieving scan data: {e}")
            return None
    
    def get_all_scans(self):
        """Get list of all scans"""
        try:
            self.cursor.execute('SELECT * FROM scans ORDER BY scan_date DESC')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[✗] Error retrieving scans: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[✓] Database connection closed")


if __name__ == "__main__":
    # Test database
    db = Database()
    print("Database module test completed successfully")
    db.close()
