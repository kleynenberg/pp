#!/bin/bash
set -e
cd "$(dirname "$0")"

# Icon: 512, 192, 180 (apple-touch)
magick -density 300 taksie-icon.svg -resize 512x512 -background "#0F1226" -flatten icon-512.png
magick -density 300 taksie-icon.svg -resize 192x192 -background "#0F1226" -flatten icon-192.png
magick -density 300 taksie-icon.svg -resize 180x180 -background "#0F1226" -flatten apple-touch-icon.png

# Maskable: safe-zone, t in het midden, 80% van de canvas
magick taksie-icon.svg -resize 512x512 -background "#0F1226" -flatten \
  -resize 410x410 -gravity center -extent 512x512 -background "#0F1226" icon-512-maskable.png

# OG: 1200x630, PNG + JPG
magick -density 300 taksie-og.svg -resize 1200x630 -background "#0F1226" -flatten og-image.png
magick -density 300 taksie-og.svg -resize 1200x630 -background "#0F1226" -flatten -quality 92 og-image.jpg

echo "Done:"
ls -lh icon-*.png apple-touch-icon.png og-image.*