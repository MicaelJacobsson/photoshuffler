#!/usr/bin/env python3
"""Generate weighted/filtered playlist from photos.db."""
import sqlite3, os, sys, random
from datetime import datetime

DB_PATH = os.path.expanduser("~/photoshuffler/photos.db")
PLAYLIST = "/tmp/photoshuffler-playlist.txt"

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Generate photo playlist with filters and bias")
    p.add_argument("--after", help="Only photos after this date (YYYY-MM-DD or YYYY)")
    p.add_argument("--before", help="Only photos before this date (YYYY-MM-DD or YYYY)")
    p.add_argument("--location", help="Filter by location (substring match)")
    p.add_argument("--album", help="Filter by album name")
    p.add_argument("--videos", action="store_true", help="Include video files")
    p.add_argument("--videos-only", action="store_true", help="Only video files")
    p.add_argument("--profile", choices=["uniform", "recent-bias"], default="uniform",
                   help="Weighting profile")
    p.add_argument("--output", default=PLAYLIST, help="Output playlist path")
    p.add_argument("--dry-run", action="store_true", help="Print stats without writing")
    return p.parse_args()

def build_query(args):
    conditions = []
    params = []
    if not args.videos and not args.videos_only:
        conditions.append("is_video = 0")
    if args.videos_only:
        conditions.append("is_video = 1")
    if args.after:
        conditions.append("creation_time >= ?")
        params.append(args.after if '-' in args.after else f"{args.after}-01-01")
    if args.before:
        conditions.append("creation_time < ?")
        params.append(args.before if '-' in args.before else f"{int(args.before)+1}-01-01")
    if args.location:
        conditions.append("location_name LIKE ?")
        params.append(f"%{args.location}%")
    if args.album:
        conditions.append("album LIKE ?")
        params.append(f"%{args.album}%")
    where = " AND ".join(conditions) if conditions else "1=1"
    return f"SELECT path, year, creation_time, location_name FROM photos WHERE {where}", params

def weight_recent_bias(year):
    """12x current year, 8x last, 4x 2y ago, 2x 3y ago, 1x rest."""
    now = datetime.now().year
    diff = now - year
    if diff == 0: return 12
    if diff == 1: return 8
    if diff == 2: return 4
    if diff == 3: return 2
    return 1

def main():
    args = parse_args()
    db = sqlite3.connect(DB_PATH)
    query, params = build_query(args)
    rows = db.execute(query, params).fetchall()
    db.close()

    if not rows:
        print("No photos match the filters.")
        sys.exit(1)

    # Apply weighting
    playlist = []
    for path, year, creation_time, location_name in rows:
        weight = weight_recent_bias(year) if args.profile == "recent-bias" else 1
        playlist.extend([path] * weight)

    random.shuffle(playlist)

    if args.dry_run:
        print(f"Matched: {len(rows)} photos → {len(playlist)} playlist entries (profile: {args.profile})")
        if args.location:
            by_year = {}
            for _, y, _, _ in rows:
                by_year[y] = by_year.get(y, 0) + 1
            for y in sorted(by_year):
                print(f"  {y}: {by_year[y]}")
        return

    with open(args.output, 'w') as f:
        f.write('\n'.join(playlist) + '\n')

    # Generate info lookup for mpv OSD
    info_path = args.output.replace("playlist", "info")
    with open(info_path, 'w') as f:
        for path, year, creation_time, location_name in rows:
            date_str = creation_time[:10] if creation_time else ""
            parts = [date_str]
            if location_name:
                # Show just city + country (first and last parts)
                loc_parts = [p.strip() for p in location_name.split(",")]
                if len(loc_parts) >= 2:
                    parts.append(f"{loc_parts[0]}, {loc_parts[-1]}")
                else:
                    parts.append(location_name)
            f.write(f"{path}\t{', '.join(p for p in parts if p)}\n")

    print(f"{len(rows)} photos → {len(playlist)} playlist entries (profile: {args.profile}) → {args.output}")

if __name__ == "__main__":
    main()
