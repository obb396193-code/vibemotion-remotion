#!/usr/bin/env bash
# Render a Remotion composition with a CLEAN chrome-headless-shell, dodging the two
# classic failures: (1) slow 93MB auto-download over a flaky proxy, (2) system Chrome
# (user profile) -> "Visited http://localhost:3001 but got no response".
#
# Usage: bash render.sh <CompId> <out.mp4> [extra `remotion render` flags...]
#   bash render.sh ArticleHighlight out/article.mp4
#
# Run from the Remotion project root (where package.json / node_modules live).

COMP="${1:?usage: render.sh <CompId> <out.mp4> [flags]}"
OUT="${2:?usage: render.sh <CompId> <out.mp4> [flags]}"
shift 2

# Prefer a clean chrome-headless-shell; fall back through known locations.
# macOS playwright cache:
BIN="$(ls -dt "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | head -1)"
# Linux playwright cache:
[ -z "$BIN" ] && BIN="$(ls -dt "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux*/chrome-headless-shell 2>/dev/null | head -1)"
# Remotion's own downloaded shell:
[ -z "$BIN" ] && BIN="$(find ./node_modules/.remotion -name chrome-headless-shell -type f 2>/dev/null | head -1)"
# full Chrome-for-Testing (mac, then linux):
[ -z "$BIN" ] && BIN="$(ls -dt "$HOME"/Library/Caches/ms-playwright/chromium-*/chrome-mac-*/"Google Chrome for Testing.app"/Contents/MacOS/"Google Chrome for Testing" 2>/dev/null | head -1)"
[ -z "$BIN" ] && BIN="$(ls -dt "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)"

if [ -z "$BIN" ]; then
  echo "No clean headless-shell found; fetching once (slow over proxy — export all_proxy=http://127.0.0.1:12000 if it stalls)..."
  npx remotion browser ensure
  BIN="$(find ./node_modules/.remotion -name chrome-headless-shell -type f 2>/dev/null | head -1)"
fi

[ -z "$BIN" ] && { echo "ERROR: no browser available"; exit 1; }
echo "Using browser: $BIN"
npx remotion render "$COMP" "$OUT" --browser-executable="$BIN" "$@"
