#!/bin/bash
# Disable screen blanking and power management
xset s off
xset -dpms
xset s noblank

exec /home/ubuntu/photoshuffler/start.sh
