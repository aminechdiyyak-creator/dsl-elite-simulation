#!/usr/bin/env bash
# macOS installer: dependencies, config, and registration in Claude Code.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

log() { echo "[install] $*"; }
die() { echo "[install] ERROR: $*" >&2; exit 1; }

[[ "$(uname)" == "Darwin" ]] || die "This script is for macOS."
command -v node >/dev/null 2>&1 || die "Node.js 18+ is required (brew install node)."
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
(( NODE_MAJOR >= 18 )) || die "Node.js 18+ is required (found $(node -v))."
[[ -x "$CHROME" ]] || die "Google Chrome is required in /Applications."

cd "$PROJECT_DIR"
log "Installing dependencies (system Chrome is used, no Playwright browser download)..."
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-fund --no-audit

if [[ ! -f config/flow.config.json ]]; then
  cp config/flow.config.mac.example.json config/flow.config.json
  read -r -p "[install] Google account used in Flow (email, optional): " EMAIL || true
  if [[ -n "${EMAIL:-}" ]]; then
    node -e 'const f="config/flow.config.json",fs=require("fs");const c=JSON.parse(fs.readFileSync(f,"utf8"));c.expectedAccount=process.argv[1];fs.writeFileSync(f,JSON.stringify(c,null,2)+"\n")' "$EMAIL"
  fi
  log "Created config/flow.config.json"
else
  log "config/flow.config.json already exists, left as is"
fi
chmod +x scripts/*.sh

if command -v claude >/dev/null 2>&1; then
  if claude mcp get google-flow >/dev/null 2>&1; then
    log "Claude Code: 'google-flow' already registered"
  else
    claude mcp add --scope user google-flow -- node "$PROJECT_DIR/src/index.js"
    log "Claude Code: 'google-flow' registered (user scope)"
  fi
else
  log "Claude Code CLI not found. Register later with:"
  log "  claude mcp add --scope user google-flow -- node \"$PROJECT_DIR/src/index.js\""
fi

log "Next: run scripts/start-browser-mac.sh, sign in to Google once in that window,"
log "then restart Claude Code and run 'claude mcp list'."
