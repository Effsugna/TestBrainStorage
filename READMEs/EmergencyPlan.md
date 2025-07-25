# 🚨 Emergency Operations Plan – MacBook Terminal Survival

> **Location:** `~/Desktop/TestBrainStorage/READMEs/EmergencyPlan.md`  
> **Author:** Angus Flavel  
> **Purpose:** Survival SOP if internet/power fails, central services collapse, or world enters emergency state

---

## 🔋 0. BOOT INSTRUCTIONS

- **If Mac won’t boot normally:**
  - Hold `Power` until you see **Options**
  - Enter **Recovery Mode**
  - Open *Terminal* from Utilities
  - Mount drive:  
    ```bash
    cd /Volumes/Macintosh\ HD/Users/angusflavel/Desktop/TestBrainStorage
    ```
  - Run emergency scripts or open manuals with `pico`, `cat`, or `bash`

---

## 🧠 1. COMMUNICATION PATHWAYS

### ✅ LAN Chat via Netcat  
*Works over local Wi-Fi with no internet*

**Start listener:**
```bash
ncat -l 8888
```

**Send message:**
```bash
ncat <IP_ADDRESS> 8888
```
> Replace `<IP_ADDRESS>` with LAN IP (e.g. `192.168.1.17`)

---

### ✅ Broadcast to Jyah (Android via Termux)

```bash
./notify_jyah.sh "Message here"
```
> Sends SSH command via port `8022` using `am broadcast` on Android

---

### ✅ Offline Mesh Comms (LoRa)

**With meshtastic device connected:**
```bash
meshtastic --info
meshtastic --sendtext "Emergency message"
```

---

## 🧭 2. MAPS & NAVIGATION

### ✅ Convert GPS Tracks:
```bash
gpsbabel -i gpx -f input.gpx -o kml -F output.kml
```

### ✅ Offline Maps (Mobile):

- OsmAnd or OrganicMaps (OpenStreetMap-based)
- Download regions in advance

---

## 🔐 3. DATA ACCESS & SECURITY

### ✅ Mount Encrypted Volume:
```bash
open -a veracrypt
```
> Then mount `Survival.vc` from `~/Documents/`

---

### ✅ Encrypt / Decrypt Messages:

**Encrypt:**
```bash
gpg --encrypt --recipient angusflavel file.txt
```

**Decrypt:**
```bash
gpg --decrypt file.txt.gpg
```

**Symmetric (passphrase only):**
```bash
gpg -c file.txt
```

---

## 📦 4. DOCUMENT & SYSTEM RESTORE

### ✅ Push Markdown to GitHub (via ngrok):

```bash
./filepush.sh "READMEs/EmergencyPlan.md"
```

### ✅ View Local Docs:

```bash
cd ~/Desktop/TestBrainStorage/READMEs
ls
pico MacBookTools.md
```

---

## 📡 5. RADIO MONITORING (SDR USB Required)

**After plugging in RTL-SDR:**

- Start GUI scanner:
  ```bash
  gqrx
  ```

- Run programmable DSP:
  ```bash
  gnuradio-companion
  ```

- Capture raw feed:
  ```bash
  rtl_sdr output.bin
  ```

---

## 🧰 6. KEY SCRIPTS

- `notify_jyah.sh` – Send local broadcast to Android
- `launch_radio.sh` – Launch radio tools
- `connect_loops.sh` – Restore WiFi, BT, or mesh links
- `mirror_sites.sh` – Mirror key websites for offline use
- `secure_docs.sh` – Batch encrypt/decrypt documents
- `gitpush.sh` – Commit and push to GitHub
- `filepush.sh` – Push one file to GitHub easily
- `blackout_mode.sh` – (coming soon)

---

## 📁 7. REDUNDANT FILE LOCATIONS

- `~/Desktop/TestBrainStorage/READMEs/` – All critical documentation
- `/Volumes/USB_BACKUP/` – External mirror
- `~/Documents/Survival.vc` – Veracrypt volume (requires GUI or CLI mount)

---

## ⚠️ FINAL REMINDERS

- **Charge battery packs**
- **Use terminal if GUI fails**
- **All tools function offline**

> If all else fails: Radio. LoRa. Sneakernet.  
> Stay sharp. Trust yourself.