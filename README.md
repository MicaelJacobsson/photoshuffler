# Photoshuffler

Fullscreen random photo slideshow for a headless Linux box (NUC) connected to a monitor.
Displays photos from a Synology NAS via SMB mount with date and location overlay.

## Features

- Shuffled slideshow of ~57,000 photos (JPG, HEIC, PNG)
- Date + reverse-geocoded location in bottom-left corner
- SQLite metadata index for fast filtering and weighted playlists
- Bias profiles (recent photos shown more often)
- Filters: date range, location, album
- Video playback support via mpv (separate mode)
- Nightly Ente sync via cron (new photos appear next day)
- Auto-starts on boot (no desktop environment)

## Requirements

- Ubuntu 24.04 Server
- Packages: xserver-xorg, xinit, feh, libimage-exiftool-perl, cifs-utils, sqlite3, python3, mpv, x11-xserver-utils
- SMB-accessible photo share (Synology NAS)
- Ente CLI for cloud sync

## Files

| File | Purpose |
|------|---------|
| photoshuffler.conf | Configuration |
| start.sh | Boot entrypoint (generates playlist + launches feh) |
| generate-playlist.py | Playlist generator with filters and bias |
| build-index.py | Builds SQLite index from Ente .meta JSON files |
| batch-geocode.py | Reverse-geocodes all GPS coords → location names |
| photo-info.sh | Per-photo info script called by feh --info |
| photo-info.lua | mpv OSD script for video mode |
| ente-sync.sh | Nightly cron: export + rebuild index + refresh playlist |
| photos.db | SQLite index (path, date, GPS, location, album) |

## Configuration

Edit `photoshuffler.conf`:

| Variable | Default | Description |
|----------|---------|-------------|
| PHOTO_DIR | /mnt/photos/ente | Path to mounted photos |
| SLIDE_DELAY | 15 | Seconds per photo |
| PHOTO_EXTENSIONS | jpg\|jpeg\|png\|heic\|heif | File types (pipe-separated) |
| PROFILE | recent-bias | Default bias profile |
| PLAYLIST | /tmp/photoshuffler-playlist.txt | Generated playlist path |

## Usage

### Change slideshow options

SSH in, generate a new playlist, restart:

```bash
ssh ubuntu@192.168.68.118

# Generate playlist with options (see below)
python3 ~/photoshuffler/generate-playlist.py --location Greece --profile recent-bias

# Restart slideshow (won't overwrite fresh playlist)
sudo systemctl restart getty@tty1
```

To return to defaults, just restart without regenerating (after >60s it'll auto-regenerate with PROFILE from config).

### Playlist generator options

```
python3 generate-playlist.py [OPTIONS]

Filters (reduce the set):
  --after DATE        Only photos after this date (YYYY-MM-DD or YYYY)
  --before DATE       Only photos before this date (YYYY-MM-DD or YYYY)
  --location TEXT     Substring match on location (case-insensitive)
  --album TEXT        Substring match on album name
  --videos-only       Only video files (.mov)

Weighting:
  --profile uniform       Equal weight (pure random)
  --profile recent-bias   12x current year, 8x last, 4x 2y, 2x 3y, 1x rest

Other:
  --output PATH       Output file (default: /tmp/photoshuffler-playlist.txt)
  --dry-run           Print stats without writing
```

### Examples

```bash
# All photos, recent bias (default)
python3 generate-playlist.py --profile recent-bias

# Only photos from Greece
python3 generate-playlist.py --location Greece

# Amorgos trip, 2025
python3 generate-playlist.py --location Amorgos --after 2025

# Last two years only
python3 generate-playlist.py --after 2024

# Uniform random (no bias)
python3 generate-playlist.py --profile uniform

# Dry run to see what matches
python3 generate-playlist.py --location Sweden --after 2020 --dry-run
```

### Play videos

Videos (26 .mov files) can't play in feh. Use mpv separately:

```bash
python3 ~/photoshuffler/generate-playlist.py --videos-only --output /tmp/videos.txt
DISPLAY=:0 mpv --fullscreen --osd-align-y=bottom --osd-align-x=left \
  --osd-level=1 --osd-font-size=36 --osd-duration=99999 \
  --script=~/photoshuffler/photo-info.lua \
  --playlist=/tmp/videos.txt
```

### Rebuild index

After manual changes to photos or metadata:

```bash
python3 ~/photoshuffler/build-index.py        # ~27 min (reads .meta JSON over SMB)
python3 ~/photoshuffler/batch-geocode.py      # ~1 sec per new unique location
```

## Nightly sync

Cron runs at 4:00 AM daily (`ente-sync.sh`):
1. Runs `ente export` (downloads new photos from Ente cloud → NAS)
2. Rebuilds SQLite index
3. Geocodes any new locations
4. If photo count changed: regenerates playlist and restarts slideshow

## Architecture

```
Boot → getty autologin → .bash_profile → startx → xinitrc → start.sh → feh
                                                              ↓
                                              generate-playlist.py (from photos.db)
```

## Location matching

Locations are stored as full hierarchy: `City, County, State, Country`

Examples in the DB:
- `Municipality of Amorgos, Naxos Regional Unit, South Aegean, Greece`
- `Stockholm, Stockholm County, Sweden`
- `Castelló d'Empúries, Alt Empordà, Catalonia, Spain`

The `--location` filter matches any part (substring, case-insensitive):
- `--location Greece` → all Greek photos
- `--location Amorgos` → just Amorgos
- `--location Sweden` → all Swedish photos
