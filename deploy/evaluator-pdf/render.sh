#!/usr/bin/env bash
# Render the single-page evaluator-mapping.pdf from HTML via headless Chrome.
# Output lands in dashboard/public/downloads/ so Vite serves it.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SRC="$HERE/source/evaluator-mapping.html"
DEST="$ROOT/dashboard/public/downloads/evaluator-mapping.pdf"

mkdir -p "$(dirname "$DEST")"

if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v chromium >/dev/null 2>&1; then
  CHROME="chromium"
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME="google-chrome"
else
  echo "No Chrome/Chromium found." >&2
  exit 1
fi

echo "→ rendering evaluator-mapping.pdf"
"$CHROME" \
  --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf="$DEST" \
  --virtual-time-budget=5000 \
  "file://$SRC" 2>&1 | tail -2

if command -v pdfinfo >/dev/null 2>&1; then
  pages=$(pdfinfo "$DEST" | awk '/^Pages:/ {print $2}')
  size=$(du -h "$DEST" | awk '{print $1}')
  echo "✓ wrote $DEST (${pages} page, ${size})"
  if [[ "$pages" != "1" ]]; then
    echo "⚠ expected 1 page, got ${pages}. Trim copy or check CSS." >&2
    exit 2
  fi
else
  echo "✓ wrote $DEST"
fi
