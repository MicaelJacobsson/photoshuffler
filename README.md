# Photoshuffler

Fullscreen random photo slideshow for a headless Linux box (NUC/Pi) connected to a monitor.
Displays photos from a Synology NAS via SMB mount with EXIF date overlay.

## Features

- Shuffled slideshow of ~57,000 photos (JPG, HEIC, PNG)
- EXIF date displayed in bottom-left corner (large font)
- Auto-starts on boot (no desktop environment needed)
- Configurable slide interval

## Requirements

- Ubuntu 24.04 Server (or similar)
- Packages: xserver-xorg, xinit, feh, libimage-exiftool-perl, cifs-utils, libheif-plugin-libde265
- SMB-accessible photo share

## Installation

1. Clone this repo to ~/photoshuffler
2. Run `sudo ./install.sh`
3. Create /etc/samba/nas-credentials with your NAS username/password
4. Edit photoshuffler.conf to set your photo directory
5. Reboot

## Configuration

Edit `photoshuffler.conf`:
- `PHOTO_DIR` — path to mounted photos
- `SLIDE_DELAY` — seconds per photo (default: 15)
- `PHOTO_EXTENSIONS` — file types to include

## Architecture

Boot → getty autologin → .bash_profile → startx → xinitrc → start.sh → feh
