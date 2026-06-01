#!/bin/bash
# Display EXIF date and location (reverse-geocoded from GPS)
CACHE_DIR="/tmp/photoshuffler-geocache"
mkdir -p "$CACHE_DIR"

# Get date
DATE=$(exiftool -d '%Y-%m-%d' -p '$DateTimeOriginal' "$1" 2>/dev/null)

# Get GPS coordinates
GPS=$(exiftool -n -p '$GPSLatitude,$GPSLongitude' "$1" 2>/dev/null)

if [ -n "$GPS" ] && [ "$GPS" != "," ]; then
    LAT=${GPS%%,*}
    LON=${GPS##*,}
    
    # Round to 2 decimals for cache key (~1km precision)
    KEY=$(printf "%.2f_%.2f" "$LAT" "$LON")
    CACHE_FILE="$CACHE_DIR/$KEY"
    
    if [ -f "$CACHE_FILE" ]; then
        LOCATION=$(cat "$CACHE_FILE")
    else
        # Reverse geocode via Nominatim
        RESULT=$(curl -s --max-time 3             "https://nominatim.openstreetmap.org/reverse?lat=$LAT&lon=$LON&format=json&zoom=10&accept-language=en"             -H 'User-Agent: photoshuffler/1.0')
        CITY=$(echo "$RESULT" | jq -r '.address.city // .address.town // .address.village // .address.municipality // empty' 2>/dev/null)
        COUNTRY=$(echo "$RESULT" | jq -r '.address.country // empty' 2>/dev/null)
        
        if [ -n "$CITY" ] && [ -n "$COUNTRY" ]; then
            LOCATION="$CITY, $COUNTRY"
        elif [ -n "$COUNTRY" ]; then
            LOCATION="$COUNTRY"
        fi
        
        # Cache the result
        echo "$LOCATION" > "$CACHE_FILE"
    fi
fi

# Output
if [ -n "$DATE" ] && [ -n "$LOCATION" ]; then
    echo "$DATE, $LOCATION"
elif [ -n "$DATE" ]; then
    echo "$DATE"
fi
