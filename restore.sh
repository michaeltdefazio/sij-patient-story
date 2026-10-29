#!/bin/bash
# Restore this project into a fresh Claude workspace so the build scripts run unchanged.
# Usage (from a clone of this branch):   bash restore.sh
# Then also clone the website (main branch) to /home/claude/sij-patient-story for publishing.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
H=/home/claude
mkdir -p $H/scripts $H/handout/design $H/handout/brochures $H/handout/up $H/handout/qr $H/handout/pdf \
         $H/handout/final/PRINT $H/handout/final/EMAIL $H/fontsrc/package/files $H/web/site $H/web/gh $H/web/gh_videos
cp "$HERE"/scripts/*.py            $H/scripts/
cp "$HERE"/design/*.html           $H/handout/design/
cp "$HERE"/brochures/*.pdf         $H/handout/brochures/
cp "$HERE"/assets/headshots/*.jpg  $H/handout/up/
cp "$HERE"/assets/qr/*             $H/handout/qr/
cp "$HERE"/assets/fonts/*.woff2    $H/fontsrc/package/files/
cp "$HERE"/assets/fonts/LICENSE      $H/fontsrc/package/LICENSE
cp "$HERE"/web/captions.vtt "$HERE"/web/brochure_bios.json "$HERE"/web/poster_hd.jpg $H/web/
cp -r "$HERE"/web/img "$HERE"/web/share $H/web/
cp "$HERE"/print/*.pdf             $H/handout/final/PRINT/
pip install --break-system-packages -q playwright img2pdf segno opencv-python-headless pypdf pillow >/dev/null 2>&1 || true
echo "Restored. Rebuild with:"
echo "  python3 -I $H/scripts/build_pdfs.py && python3 -I $H/scripts/build_final.py      # handouts (PRINT + EMAIL)"
echo "  SITE_REPO=sij-patient-story python3 -I $H/scripts/build_site.py                  # website into $H/web/gh/"
