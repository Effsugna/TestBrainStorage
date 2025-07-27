#!/bin/bash

mkdir -p scans

interfaces=$(ifconfig | grep -E '^[a-z0-9]+:' | cut -d: -f1)

for iface in $interfaces; do
  ip=$(ipconfig getifaddr "$iface" 2>/dev/null)
  if [[ -n "$ip" ]]; then
    subnet="${ip%.*}.0/24"
    echo "🌐 Scanning subnet $subnet on interface $iface..."
    sudo nmap -T4 -A -v --disable-arp-ping -PE -PS22,25,80 "$subnet" -oX "scans/$iface.xml"
    /opt/homebrew/opt/libxslt/bin/xsltproc "scans/$iface.xml" -o "scans/$iface.html"
  fi
done

echo -e "\n🌐 Opening all scan results..."
open scans/*.html

