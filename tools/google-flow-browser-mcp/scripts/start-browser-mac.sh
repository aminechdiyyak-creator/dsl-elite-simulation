#!/usr/bin/env bash
# macOS: open Chrome on Google Flow with the MCP's dedicated profile and CDP on 127.0.0.1:9222.
# First run: sign in to Google in the window that opens (one time), then use the MCP.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$PROJECT_DIR/config/flow.config.json"

cfg() { node -e 'const c=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));const v=c[process.argv[2]];process.stdout.write(v===undefined?"":String(v))' "$CONFIG" "$1" 2>/dev/null || true; }

CHROME="$(cfg chromePath)"; CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
USER_DATA_DIR="$(cfg chromeUserDataDir)"; USER_DATA_DIR="${USER_DATA_DIR:-$HOME/.google-flow-mcp/chrome-profile}"
USER_DATA_DIR="${USER_DATA_DIR/#\~/$HOME}"
PROFILE="$(cfg chromeProfile)"; PROFILE="${PROFILE:-Default}"
CDP_PORT="$(cfg cdpPort)"; CDP_PORT="${CDP_PORT:-9222}"
FLOW_URL="$(cfg flowUrl)"; FLOW_URL="${FLOW_URL:-https://labs.google/fx/fr/tools/flow}"

log() { echo "[start-browser] $*" >&2; }
die() { echo "[start-browser] ERROR: $*" >&2; exit 1; }

[[ -x "$CHROME" ]] || die "Google Chrome not found at: $CHROME"

if curl -s "http://127.0.0.1:$CDP_PORT/json/version" >/dev/null 2>&1; then
  log "Chrome already listening on CDP port $CDP_PORT"
  exit 0
fi
if lsof -ti "tcp:$CDP_PORT" >/dev/null 2>&1; then
  die "Port $CDP_PORT is used by another program (lsof -i tcp:$CDP_PORT). Free it or change cdpPort."
fi

mkdir -p "$USER_DATA_DIR"
log "Launching Chrome (profile: $USER_DATA_DIR / $PROFILE, CDP 127.0.0.1:$CDP_PORT)"
"$CHROME" \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="$PROFILE" \
  --remote-debugging-port="$CDP_PORT" \
  --remote-debugging-address=127.0.0.1 \
  --no-first-run \
  --no-default-browser-check \
  "$FLOW_URL" >/dev/null 2>&1 &

for _ in $(seq 1 20); do
  if curl -s "http://127.0.0.1:$CDP_PORT/json/version" >/dev/null 2>&1; then
    log "Ready. If Google asks you to sign in, do it once in this window."
    exit 0
  fi
  sleep 1
done
die "Chrome did not open CDP port $CDP_PORT within 20 s"
