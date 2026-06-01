#!/bin/bash
exiftool -d '%Y-%m-%d' -p '$DateTimeOriginal' "$1" 2>/dev/null || echo ''
