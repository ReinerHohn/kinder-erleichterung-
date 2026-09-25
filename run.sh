#!/bin/sh
# Baut den Katalog und oeffnet das Dashboard.
cd "$(dirname "$0")"
python3 build.py && python3 test.py && xdg-open dashboard.html 2>/dev/null || echo "dashboard.html gebaut."
