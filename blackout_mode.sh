#!/bin/bash

echo "🔌 Entering Blackout Mode..."

# Step 1: Open EmergencyPlan
echo "📖 Opening EmergencyPlan.md..."
pico ~/Desktop/TestBrainStorage/READMEs/EmergencyPlan.md

# Step 2: Mount Encrypted Volume (Veracrypt GUI must be installed)
echo "🔐 Attempting to open Veracrypt..."
open -a veracrypt

echo "📦 Waiting for Veracrypt volume to mount..."

# Wait until /Volumes/Survival appears (max 20s)
for i in {1..20}; do
  if [ -d /Volumes/Survival ]; then
    echo "🗂 Encrypted volume detected. Starting mirror..."
    ~/Desktop/TestBrainStorage/mirror_backup.sh &
    break
  fi
  sleep 1
done

# Step 3: Launch tmux survival session
echo "🖥️ Launching tmux 'survival' session..."
tmux new-session -d -s survival
tmux send-keys -t survival 'cd ~/Desktop/TestBrainStorage' C-m
tmux send-keys -t survival './notify_jyah.sh "Blackout mode active"' C-m
tmux send-keys -t survival 'echo Radio? Plug in RTL. Then run gqrx.' C-m

# Step 4: Network check
echo "📡 Checking LAN visibility..."
if ping -c 1 192.168.1.1 &> /dev/null; then
  echo "✅ LAN Reachable"
else
  echo "⚠️ LAN Unreachable – check mesh or SDR options"
fi

# Step 5: SDR hint if USB connected (manual step prompt)
echo "🔊 Reminder: Plug in RTL-SDR dongle if radio needed"

# Final: Attach tmux
echo "🧠 Attaching to tmux 'survival' session..."
tmux send-keys -t survival 'reset' C-m
tmux send-keys -t survival 'clear' C-m
tmux send-keys -t survival 'echo 🛡  Survival session ready. Plug in RTL and run gqrx.' C-m
tmux attach-session -t survival

