#!/usr/bin/env python3
"""Batch reverse-geocode all unique coords and add location columns to photos.db."""
import sqlite3, time, json, urllib.request, os

DB_PATH = os.path.expanduser("~/photoshuffler/photos.db")
CACHE_DIR = "/tmp/photoshuffler-geocache-full"
os.makedirs(CACHE_DIR, exist_ok=True)

db = sqlite3.connect(DB_PATH)

# Add location column if missing
try:
    db.execute("ALTER TABLE photos ADD COLUMN location_name TEXT")
except sqlite3.OperationalError:
    pass

# Get unique rounded coords
rows = db.execute("""
    SELECT DISTINCT printf('%.2f', latitude) as lat, printf('%.2f', longitude) as lon
    FROM photos WHERE latitude IS NOT NULL
""").fetchall()

print(f"{len(rows)} unique coords to geocode")

def geocode(lat, lon):
    key = f"{lat}_{lon}"
    cache_file = os.path.join(CACHE_DIR, key)
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=10&accept-language=en"
    req = urllib.request.Request(url, headers={"User-Agent": "photoshuffler/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        addr = data.get("address", {})
        result = {
            "city": addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or "",
            "county": addr.get("county") or addr.get("island") or addr.get("state_district") or "",
            "state": addr.get("state") or addr.get("region") or "",
            "country": addr.get("country") or "",
        }
    except Exception as e:
        result = {"city": "", "county": "", "state": "", "country": ""}
    with open(cache_file, "w") as f:
        json.dump(result, f)
    time.sleep(1.1)  # respect rate limit
    return result

done = 0
cached = 0
for lat, lon in rows:
    key = f"{lat}_{lon}"
    cache_file = os.path.join(CACHE_DIR, key)
    is_cached = os.path.exists(cache_file)
    result = geocode(lat, lon)
    # Build searchable location string: "City, County, State, Country"
    parts = [v for v in [result["city"], result["county"], result["state"], result["country"]] if v]
    location_name = ", ".join(parts)
    # Update all photos with these rounded coords
    db.execute("""
        UPDATE photos SET location_name = ?
        WHERE printf('%.2f', latitude) = ? AND printf('%.2f', longitude) = ?
    """, (location_name, lat, lon))
    done += 1
    if is_cached:
        cached += 1
    if done % 50 == 0:
        db.commit()
        print(f"  {done}/{len(rows)} ({cached} from cache)")

db.commit()
db.close()
print(f"Done: {done} locations geocoded ({cached} from cache)")
