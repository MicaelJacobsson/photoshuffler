#!/bin/bash
set -e

# Install packages
apt-get update -qq
apt-get install -y xserver-xorg xinit feh libimage-exiftool-perl cifs-utils libheif-plugin-libde265

# SMB mount
mkdir -p /mnt/photos
if ! grep -q '/mnt/photos' /etc/fstab; then
    echo '//192.168.68.119/photo /mnt/photos cifs credentials=/etc/samba/nas-credentials,iocharset=utf8,uid=1000,gid=1000,nofail,_netdev 0 0' >> /etc/fstab
fi

# Auto-login on tty1
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << 'CONF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ubuntu --noclear %I $TERM
CONF

# Allow non-root X
cat > /etc/X11/Xwrapper.config << 'CONF'
allowed_users=anybody
needs_root_rights=yes
CONF

# Auto-start X from bash_profile
PROFILE="/home/ubuntu/.bash_profile"
if ! grep -q photoshuffler "$PROFILE" 2>/dev/null; then
    cat > "$PROFILE" << 'PROF'
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    exec startx /home/ubuntu/photoshuffler/xinitrc
fi
PROF
    chown ubuntu:ubuntu "$PROFILE"
fi

systemctl daemon-reload
echo "Done. Create /etc/samba/nas-credentials and reboot."
