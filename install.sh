#!/bin/bash

#############################################################################
# AutoPentestX Installation Script
# Installs all dependencies for Kali Linux and Ubuntu
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                 AutoPentestX Installer v1.0                   ║
║          Automated Penetration Testing Toolkit               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}[!] This script should NOT be run as root${NC}"
   echo -e "${YELLOW}[!] Please run without sudo. It will ask for password when needed.${NC}"
   exit 1
fi

echo -e "${GREEN}[*] Starting AutoPentestX installation...${NC}\n"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo -e "${RED}[✗] Cannot detect operating system${NC}"
    exit 1
fi

echo -e "${BLUE}[i] Detected OS: $OS $VER${NC}\n"

# Update package lists
echo -e "${GREEN}[*] Updating package lists...${NC}"
sudo apt-get update

# Install system dependencies
echo -e "\n${GREEN}[*] Installing system dependencies...${NC}"

PACKAGES=(
    "python3"
    "python3-pip"
    "python3-venv"
    "nmap"
    "nikto"
    "sqlmap"
    "git"
    "curl"
    "wget"
)

for package in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $package "; then
        echo -e "${GREEN}[✓] $package is already installed${NC}"
    else
        echo -e "${YELLOW}[*] Installing $package...${NC}"
        sudo apt-get install -y $package
        echo -e "${GREEN}[✓] $package installed${NC}"
    fi
done

# Check for Metasploit (optional)
echo -e "\n${GREEN}[*] Checking for Metasploit Framework...${NC}"
if command -v msfconsole &> /dev/null; then
    echo -e "${GREEN}[✓] Metasploit Framework is installed${NC}"
else
    echo -e "${YELLOW}[!] Metasploit Framework not found${NC}"
    echo -e "${YELLOW}[!] Exploitation features will be limited${NC}"
    read -p "Do you want to install Metasploit? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}[*] Installing Metasploit Framework...${NC}"
        curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
        chmod 755 msfinstall
        sudo ./msfinstall
        rm msfinstall
        echo -e "${GREEN}[✓] Metasploit Framework installed${NC}"
    fi
fi

# Create Python virtual environment
echo -e "\n${GREEN}[*] Setting up Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}[!] Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}[✓] Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
fi

# Activate virtual environment and install Python packages
echo -e "\n${GREEN}[*] Installing Python dependencies...${NC}"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[✓] Python dependencies installed${NC}"
else
    echo -e "${RED}[✗] requirements.txt not found${NC}"
    exit 1
fi

# Create necessary directories
echo -e "\n${GREEN}[*] Creating project directories...${NC}"
mkdir -p reports logs database exploits

echo -e "${GREEN}[✓] Directories created${NC}"

# Set permissions
echo -e "\n${GREEN}[*] Setting permissions...${NC}"
chmod +x main.py
chmod +x autopentestx.sh
chmod -R 755 modules/

echo -e "${GREEN}[✓] Permissions set${NC}"

# Test imports
echo -e "\n${GREEN}[*] Testing Python modules...${NC}"
python3 -c "
try:
    import nmap
    import requests
    from reportlab.lib.pagesizes import letter
    import sqlite3
    print('✓ All Python modules imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] Python modules test passed${NC}"
else
    echo -e "${RED}[✗] Python modules test failed${NC}"
    exit 1
fi

# Test database initialization
echo -e "\n${GREEN}[*] Testing database initialization...${NC}"
python3 -c "
from modules.database import Database
try:
    db = Database()
    db.close()
    print('✓ Database initialized successfully')
except Exception as e:
    print(f'✗ Database error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] Database test passed${NC}"
else
    echo -e "${RED}[✗] Database test failed${NC}"
    exit 1
fi

deactivate

# Installation complete
echo -e "\n${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║              Installation Completed Successfully!             ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}[i] AutoPentestX has been installed successfully!${NC}\n"

echo -e "${YELLOW}IMPORTANT NOTES:${NC}"
echo -e "1. Activate virtual environment: ${GREEN}source venv/bin/activate${NC}"
echo -e "2. Run the tool: ${GREEN}python3 main.py -t <target>${NC}"
echo -e "3. Or use wrapper: ${GREEN}./autopentestx.sh <target>${NC}"
echo -e "4. Get help: ${GREEN}python3 main.py --help${NC}\n"

echo -e "${YELLOW}LEGAL WARNING:${NC}"
echo -e "This tool is for AUTHORIZED testing and EDUCATIONAL purposes ONLY."
echo -e "Unauthorized access to computer systems is ILLEGAL!"
echo -e "Always obtain proper authorization before testing.\n"

echo -e "${BLUE}[i] For more information, see README.md${NC}\n"

# Ask to run a test
read -p "Do you want to run a quick test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}[*] Running quick test on localhost...${NC}"
    source venv/bin/activate
    python3 main.py -t 127.0.0.1 --skip-web --skip-exploit
fi

echo -e "\n${GREEN}[✓] Installation complete. Happy hacking (ethically)!${NC}\n"
