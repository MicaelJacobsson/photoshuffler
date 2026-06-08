#!/bin/bash
# Ente export + incremental index update + playlist refresh
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/photoshuffler.conf"

export ENTE_CLI_SECRETS_PATH=/home/ubuntu/.config/ente/.secrets

# Known count from current playlist
BEFORE=$(wc -l < "$PLAYLIST" 2>/dev/null || echo 0)

# Run export
/usr/local/bin/ente export

# Incremental index update
python3 "$DIR/update-index.py"

# Geocode any new locations
python3 "$DIR/batch-geocode.py"

# Regenerate playlist
python3 "$DIR/generate-playlist.py" --profile "${PROFILE:-recent-bias}"
AFTER=$(wc -l < "$PLAYLIST")

echo "$(date): before=$BEFORE after=$AFTER"

if [ "$AFTER" -ne "$BEFORE" ]; then
    echo "Playlist changed, restarting slideshow..."
    sudo systemctl restart getty@tty1
fi
