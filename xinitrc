#!/bin/bash
# Disable all screen blanking and power management
xset s off
xset s noblank
xset s 0 0
xset dpms 0 0 0
xset -dpms

exec /home/ubuntu/photoshuffler/start.sh
