#!/bin/bash
# Photoshuffler - fullscreen random photo slideshow with EXIF date overlay
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/photoshuffler.conf"

# Wait for mount
for i in $(seq 1 30); do
    mountpoint -q "$(dirname "$PHOTO_DIR")" && break
    sleep 2
done

# Generate shuffled playlist
find "$PHOTO_DIR" -type f -regextype posix-extended     -iregex ".*\.($PHOTO_EXTENSIONS)" > "$PLAYLIST.tmp"
shuf "$PLAYLIST.tmp" > "$PLAYLIST"
rm -f "$PLAYLIST.tmp"

echo "Playlist: $(wc -l < "$PLAYLIST") photos"

# Launch feh
exec feh --fontpath /usr/share/fonts/truetype/dejavu     --fullscreen --auto-zoom --hide-pointer     --slideshow-delay "$SLIDE_DELAY"     --font "DejaVuSans/36"     --info "$DIR/photo-info.sh %F"     --filelist "$PLAYLIST"
