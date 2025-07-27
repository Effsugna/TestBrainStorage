#!/bin/bash

# Get local IP and derive subnet
LOCAL_IP=$(ipconfig getifaddr $(route get default | awk '/interface: / {print $2}'))
SUBNET=$(echo "$LOCAL_IP" | sed 's/\.[0-9]*$/\.0\/24/')

# Confirm or prompt for subnet
echo "Detected local IP: $LOCAL_IP"
echo "Suggesting subnet: $SUBNET"
read -p "Use this subnet? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  read -p "Enter custom subnet (e.g. 192.168.0.0/24): " SUBNET
fi

# Run scan and generate visualisation
sudo nmap -T4 -A -v --disable-arp-ping -PE -PS22,25,80 "$SUBNET" -oX scan.xml
/opt/homebrew/opt/libxslt/bin/xsltproc scan.xml -o scan.html && open scan.html

