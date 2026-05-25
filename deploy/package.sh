#!/usr/bin/env bash
# package.sh — rebuild dashboard and produce a deployable tarball.
#
# Usage:  ./deploy/package.sh
# Output: cantinaiq-dashboard.tar.gz in the repo root.
#
# The tarball contains the contents of dashboard/dist/ — no leading
# directory — so it untars directly into your webroot:
#
#   sudo tar -xzf cantinaiq-dashboard.tar.gz -C /var/www/cantinaiq

set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
DASHBOARD="$HERE/dashboard"
OUT="$HERE/cantinaiq-dashboard.tar.gz"

if [[ ! -d "$DASHBOARD" ]]; then
  echo "✗ dashboard/ not found at $DASHBOARD" >&2
  exit 1
fi

echo "→ building dashboard"
cd "$DASHBOARD"
if [[ ! -d node_modules ]]; then
  echo "  installing dependencies"
  npm install --silent
fi
npm run build 2>&1 | tail -6

echo "→ packing dist/ into tarball"
cd "$DASHBOARD/dist"
tar -czf "$OUT" .

size=$(du -h "$OUT" | awk '{print $1}')
echo "✓ wrote $OUT (${size})"
echo
echo "Next steps:"
echo "  scp $OUT  user@hetzner:/tmp/"
echo "  ssh user@hetzner 'sudo tar -xzf /tmp/cantinaiq-dashboard.tar.gz -C /var/www/cantinaiq --overwrite'"
