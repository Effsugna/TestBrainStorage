

MACBOOK WWIII TOOLKIT

TERMINAL MESSAGING + LOCAL COMMS

    ncat (netcat):
    Direct message to another machine over LAN
    Use: ncat <ip> <port>
    Example: ncat 192.168.1.101 8888

    socat:
    Port forwarding, serial to network bridges
    Example: socat - TCP:<ip>:<port>

    tmux:
    Persistent terminal sessions
    Use: tmux, tmux new -s <name>, tmux attach

    screen:
    Similar to tmux, older
    Use: screen, screen -r

RADIO + MESH

    meshtastic:
    CLI for LoRa mesh radios. Needs external device.
    Use: meshtastic --sendtext "message"
    Communicates over long range with no towers

    gnuradio, gqrx, rtl-sdr:
    Software-defined radio tools.
    Use to scan AM/FM, HAM, VHF/UHF, airbands, weather, emergency radio
    Needs USB SDR dongle
    gqrx = GUI scanner
    rtl_sdr = raw capture
    gnuradio-companion = programmable flows

GPS + MAPPING

    gpsbabel:
    Converts GPS data formats.
    Use to import/export from GPS devices or map files

    OsmAnd / OrganicMaps (phone):
    Offline OpenStreetMap data for navigation
    Download regions in advance

OFFLINE KNOWLEDGE

    kiwix:
    Read .zim files (Wikipedia, Stack Overflow, medical books) offline
    Use GUI app or CLI reader
    Example files: wikipedia_en_all.zim, stackoverflow.zim

    lynx, w3m:
    Terminal web browsers.
    Use to view saved .html files or offline sites
    Use: lynx index.html

    wget, httrack:
    Mirror websites in advance
    Example: wget -m https://example.com

ENCRYPTION + DATA SECURITY

    veracrypt:
    Create encrypted file containers or volumes
    GUI or CLI
    Use to store ID, plans, passports, keys offline

    gnupg:
    Encrypt/sign messages or files
    Use: gpg -c file.txt (symmetric)
    gpg --encrypt --recipient <key> file (asymmetric)

NETWORK / TUNNELING

    wireguard-go:
    Lightweight VPN tunnel. Peer-to-peer secure link
    Use with config files .conf

    openvpn:
    Resilient VPN, supports older infra
    Use with .ovpn config files

    i2pd:
    CLI access to I2P (darknet).
    Use to host/visit services without internet

SCRIPTABLE EMERGENCY TASKS (EXAMPLES)

    ./notify_jyah.sh
    Sends SSH command to Android Termux via port 8022
    Example:
    ssh user@192.168.1.x -p 8022 am broadcast -a android.intent.action.SEND -e msg "msg"

    ./launch_radio.sh
    Opens SDR scanner tools or starts RTL readout

    ./connect_loops.sh
    Ping/reconnect loop for WiFi, BT, mesh

    ./mirror_sites.sh
    Backup critical websites regularly

    ./secure_docs.sh
    Batch encrypt or decrypt critical files

OTHER TOOLS

    nmap:
    Scan local network to discover devices
    Use: nmap -sP 192.168.1.0/24

    mosh:
    Better SSH over unstable connections

    wireguard:
    If any connection remains, use for stealth tunnel

FILES TO PREP OFFLINE

    Kiwix .zim files:

        Wikipedia (90GB)

        Stack Overflow (35GB)

        WikiHow / Medical / Wikibooks

    PDF survival guides, offline maps, radio frequencies, key contacts, SSH keys

NOTES

    If internet dies, use LAN, LoRa, radio, SDR, or sneakernet (USB).

    Use tmux or screen to maintain running sessions.

    All messaging can be done without internet if mesh or local.