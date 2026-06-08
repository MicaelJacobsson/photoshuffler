#!/bin/bash
# Photoshuffler - fullscreen random photo slideshow
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/photoshuffler.conf"

# Wait for mount
for i in $(seq 1 30); do
    mountpoint -q "$(dirname "$PHOTO_DIR")" && break
    sleep 2
done

# Generate playlist only if missing or older than 60s (skip if just regenerated manually)
if [ ! -f "$PLAYLIST" ] || [ $(( $(date +%s) - $(stat -c %Y "$PLAYLIST") )) -gt 60 ]; then
    if [ -f "$DIR/photos.db" ]; then
        python3 "$DIR/generate-playlist.py" --profile "${PROFILE:-recent-bias}"
    else
        find "$PHOTO_DIR" -type f -regextype posix-extended \
            -iregex ".*\.($PHOTO_EXTENSIONS)" | shuf > "$PLAYLIST"
    fi
fi

echo "Playlist: $(wc -l < "$PLAYLIST") entries"

# Launch feh
exec feh --fontpath /usr/share/fonts/truetype/dejavu \
    --fullscreen --auto-zoom --hide-pointer \
    --slideshow-delay "$SLIDE_DELAY" \
    --font "DejaVuSans/36" \
    --info "$DIR/photo-info.sh %F" \
    \
    --filelist "$PLAYLIST"
