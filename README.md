# Photoshuffler

Fullscreen random photo slideshow for a headless Linux box (NUC/Pi) connected to a monitor.
Displays photos from a Synology NAS via SMB mount with EXIF date overlay.

## Features

- Shuffled slideshow of ~57,000 photos (JPG, HEIC, PNG)
- EXIF date displayed in bottom-left corner (large font)
- Auto-starts on boot (no desktop environment needed)
- Configurable slide interval and file types

## Requirements

- Ubuntu 24.04 Server (or similar)
- Packages: xserver-xorg, xinit, feh, libimage-exiftool-perl, cifs-utils, libheif-plugin-libde265
- SMB-accessible photo share

## Installation

1. Clone this repo to ~/photoshuffler
2. Run `sudo ./install.sh`
3. Create /etc/samba/nas-credentials with your NAS username/password:
   ```
   username=your_user
   password=your_password
   ```
4. Edit photoshuffler.conf to set your photo directory
5. Reboot

## Configuration

Edit `photoshuffler.conf`:

| Variable | Default | Description |
|----------|---------|-------------|
| PHOTO_DIR | /mnt/photos/icloud | Path to mounted photos |
| SLIDE_DELAY | 15 | Seconds per photo |
| PHOTO_EXTENSIONS | jpg\|jpeg\|png\|heic\|heif | File types (pipe-separated regex) |
| PLAYLIST | /tmp/photoshuffler-playlist.txt | Generated playlist path |

## Changing Settings

Via SSH:
```bash
ssh ubuntu@192.168.68.118
nano ~/photoshuffler/photoshuffler.conf
sudo systemctl restart getty@tty1
```

Or via keyboard on the NUC: press Ctrl+Alt+F2 for a second tty, log in, edit, then:
```bash
sudo systemctl restart getty@tty1
```

The restart regenerates the playlist and relaunches feh with new settings.

## Architecture

Boot → getty autologin → .bash_profile → startx → xinitrc → start.sh → feh
