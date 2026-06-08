#!/bin/bash
# Display date + location from SQLite index (no EXIF/network needed)
DB="$HOME/photoshuffler/photos.db"
INFO=$(sqlite3 "$DB" "SELECT creation_time, location_name FROM photos WHERE path='$1'" 2>/dev/null)
[ -z "$INFO" ] && exit 0
DATE="${INFO%%|*}"
DATE="${DATE:0:10}"
LOC="${INFO#*|}"
if [ -n "$LOC" ]; then
    # Show first and last part (city, country)
    CITY=$(echo "$LOC" | cut -d',' -f1)
    COUNTRY=$(echo "$LOC" | rev | cut -d',' -f1 | rev | xargs)
    echo "$DATE, $CITY, $COUNTRY"
else
    echo "$DATE"
fi
