#!/usr/bin/env python3
"""
AutoPentestX - Quick Test Script
Verify installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test all required Python imports"""
    print("[*] Testing Python imports...")
    
    try:
        import nmap
        print("  [✓] python-nmap imported")
    except ImportError as e:
        print(f"  [✗] python-nmap import failed: {e}")
        return False
    
    try:
        import requests
        print("  [✓] requests imported")
    except ImportError as e:
        print(f"  [✗] requests import failed: {e}")
        return False
    
    try:
        from reportlab.lib.pagesizes import letter
        print("  [✓] reportlab imported")
    except ImportError as e:
        print(f"  [✗] reportlab import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("  [✓] sqlite3 imported")
    except ImportError:
        print(f"  [✗] sqlite3 import failed")
        return False
    
    return True

def test_modules():
    """Test AutoPentestX modules"""
    print("\n[*] Testing AutoPentestX modules...")
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from modules.database import Database
        print("  [✓] database module loaded")
    except Exception as e:
        print(f"  [✗] database module failed: {e}")
        return False
    
    try:
        from modules.scanner import Scanner
        print("  [✓] scanner module loaded")
    except Exception as e:
        print(f"  [✗] scanner module failed: {e}")
        return False
    
    try:
        from modules.vuln_scanner import VulnerabilityScanner
        print("  [✓] vuln_scanner module loaded")
    except Exception as e:
        print(f"  [✗] vuln_scanner module failed: {e}")
        return False
    
    try:
        from modules.cve_lookup import CVELookup
        print("  [✓] cve_lookup module loaded")
    except Exception as e:
        print(f"  [✗] cve_lookup module failed: {e}")
        return False
    
    try:
        from modules.risk_engine import RiskEngine
        print("  [✓] risk_engine module loaded")
    except Exception as e:
        print(f"  [✗] risk_engine module failed: {e}")
        return False
    
    try:
        from modules.exploit_engine import ExploitEngine
        print("  [✓] exploit_engine module loaded")
    except Exception as e:
        print(f"  [✗] exploit_engine module failed: {e}")
        return False
    
    try:
        from modules.pdf_report import PDFReportGenerator
        print("  [✓] pdf_report module loaded")
    except Exception as e:
        print(f"  [✗] pdf_report module failed: {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\n[*] Testing database...")
    
    try:
        from modules.database import Database
        db = Database("database/test.db")
        db.close()
        os.remove("database/test.db")
        print("  [✓] database initialization successful")
        return True
    except Exception as e:
        print(f"  [✗] database test failed: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("\n[*] Testing directories...")
    
    dirs = ['modules', 'reports', 'logs', 'database', 'exploits']
    
    for d in dirs:
        if os.path.exists(d):
            print(f"  [✓] {d}/ exists")
        else:
            print(f"  [✗] {d}/ missing")
            return False
    
    return True

def test_files():
    """Test required files"""
    print("\n[*] Testing required files...")
    
    files = [
        'main.py',
        'config.json',
        'requirements.txt',
        'README.md',
        'DISCLAIMER.md',
        'LICENSE'
    ]
    
    for f in files:
        if os.path.exists(f):
            print(f"  [✓] {f} exists")
        else:
            print(f"  [✗] {f} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AutoPentestX - Installation Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Python Imports", test_imports()))
    results.append(("AutoPentestX Modules", test_modules()))
    results.append(("Database", test_database()))
    results.append(("Directories", test_directories()))
    results.append(("Required Files", test_files()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  [{symbol}] {test_name}: {status}")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print("\n[✓] All tests passed! AutoPentestX is ready to use.")
        print("\nTo run a scan:")
        print("  python3 main.py -t <target>")
        print("\nOr use the wrapper:")
        print("  ./autopentestx.sh <target>")
        return 0
    else:
        print("\n[✗] Some tests failed. Please check the installation.")
        print("\nTry running:")
        print("  ./install.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())
