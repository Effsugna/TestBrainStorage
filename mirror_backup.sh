#!/bin/bash

echo "🪞 MIRRORING BACKUP NOW"
DATE=$(date "+%Y-%m-%d_%H-%M")
LOG="mirror_log_$DATE.txt"

# Target 1: Veracrypt Volume
if [ -d /Volumes/Survival ]; then
  echo "→ Backing up to Veracrypt volume..."
  rsync -a --delete ~/Desktop/TestBrainStorage/ /Volumes/Survival/TestBrainStorage_Backup/ >> "$LOG"
else
  echo "⚠️ Veracrypt volume not found."
fi

# Save the log
mv "$LOG" ~/Desktop/TestBrainStorage/backup_logs/"$LOG"
echo "✅ Backup complete. Log saved to backup_logs/$LOG"

