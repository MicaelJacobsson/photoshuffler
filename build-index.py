#!/usr/bin/env python3
"""Build SQLite index from Ente .meta/*.json files."""
import json, os, sqlite3, sys
from pathlib import Path

PHOTO_DIR = sys.argv[1] if len(sys.argv) > 1 else "/mnt/photos/ente"
DB_PATH = os.path.expanduser("~/photoshuffler/photos.db")

db = sqlite3.connect(DB_PATH)
db.execute("DROP TABLE IF EXISTS photos")
db.execute("""CREATE TABLE photos (
    path TEXT PRIMARY KEY,
    filename TEXT,
    creation_time TEXT,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    latitude REAL,
    longitude REAL,
    album TEXT,
    is_video INTEGER DEFAULT 0
)""")
db.execute("CREATE INDEX idx_year ON photos(year)")
db.execute("CREATE INDEX idx_coords ON photos(latitude, longitude)")

EXTENSIONS = {'.jpg','.jpeg','.png','.heic','.heif','.mov','.mp4'}
count = 0
errors = 0

for root, dirs, files in os.walk(PHOTO_DIR):
    if not root.endswith('.meta'):
        continue
    album = Path(root).parent.name
    for f in files:
        if not f.endswith('.json'):
            continue
        meta_path = os.path.join(root, f)
        # Derive the actual media file path
        media_name = f[:-5]  # strip .json
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
            # Parse date parts from ISO string
            year = int(ct[:4])
            month = int(ct[5:7])
            day = int(ct[8:10])
            loc = meta.get("location") or {}
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            is_video = 1 if ext in ('.mov', '.mp4') else 0
            db.execute("INSERT OR REPLACE INTO photos VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (media_path, media_name, ct, year, month, day, lat, lon, album, is_video))
            count += 1
        except (json.JSONDecodeError, KeyError, ValueError):
            errors += 1

db.commit()
db.close()
print(f"Indexed {count} files ({errors} errors) → {DB_PATH}")
