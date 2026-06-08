#!/usr/bin/env python3
"""Incremental update of photos.db from Ente .meta/*.json files.
Only processes files modified since last run."""
import json, os, sqlite3, sys, time
from pathlib import Path

PHOTO_DIR = sys.argv[1] if len(sys.argv) > 1 else "/mnt/photos/ente"
DB_PATH = os.path.expanduser("~/photoshuffler/photos.db")
STAMP_FILE = os.path.expanduser("~/photoshuffler/.last-index-time")

# Get last run timestamp
last_run = 0
if os.path.exists(STAMP_FILE):
    last_run = os.path.getmtime(STAMP_FILE)

db = sqlite3.connect(DB_PATH)

# Ensure table exists (first run handled by build-index.py)
try:
    db.execute("SELECT count(*) FROM photos")
except sqlite3.OperationalError:
    print("No database found. Run build-index.py first.")
    sys.exit(1)

EXTENSIONS = {'.jpg','.jpeg','.png','.heic','.heif','.mov','.mp4'}
updated = 0
errors = 0

for root, dirs, files in os.walk(PHOTO_DIR):
    if not root.endswith('.meta'):
        continue
    album = Path(root).parent.name
    for f in files:
        if not f.endswith('.json'):
            continue
        meta_path = os.path.join(root, f)
        # Skip if not modified since last run
        if os.path.getmtime(meta_path) <= last_run:
            continue
        media_name = f[:-5]
        media_path = os.path.join(Path(root).parent, media_name)
        ext = os.path.splitext(media_name)[1].lower()
        if ext not in EXTENSIONS:
            continue
        if not os.path.exists(media_path):
            continue
        try:
            with open(meta_path) as fh:
                meta = json.load(fh)
            ct = meta.get("creationTime")
            if not ct:
                continue
            year = int(ct[:4])
            month = int(ct[5:7])
            day = int(ct[8:10])
            loc = meta.get("location") or {}
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            is_video = 1 if ext in ('.mov', '.mp4') else 0
            db.execute("INSERT OR REPLACE INTO photos (path,filename,creation_time,year,month,day,latitude,longitude,album,is_video) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (media_path, media_name, ct, year, month, day, lat, lon, album, is_video))
            updated += 1
        except (json.JSONDecodeError, KeyError, ValueError):
            errors += 1

db.commit()
db.close()

# Update timestamp
Path(STAMP_FILE).touch()

if updated > 0 or errors > 0:
    print(f"Updated {updated} entries ({errors} errors)")
else:
    print("No changes")
