#!/usr/bin/env bash
# Re-render brief.pdf from brief.html via headless Chrome.
# Usage: ./render.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/source/brief.html"
OUT="$HERE/source/brief.pdf"

# Find a Chromium-derived browser.
if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v chromium >/dev/null 2>&1; then
  CHROME="chromium"
elif command -v chromium-browser >/dev/null 2>&1; then
  CHROME="chromium-browser"
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME="google-chrome"
else
  echo "No Chrome/Chromium found. Install one or use WeasyPrint." >&2
  exit 1
fi

echo "→ rendering with: $CHROME"
"$CHROME" \
  --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf="$OUT" \
  --virtual-time-budget=5000 \
  "file://$SRC" 2>&1 | tail -2

if command -v pdfinfo >/dev/null 2>&1; then
  pages=$(pdfinfo "$OUT" | awk '/^Pages:/ {print $2}')
  echo "✓ wrote $OUT (${pages} pages)"
  if [[ "$pages" != "22" ]]; then
    echo "⚠ page count is ${pages}, not 22. Tighten copy or check CSS knobs." >&2
    exit 2
  fi
else
  echo "✓ wrote $OUT (install poppler-utils for page-count check)"
fi
