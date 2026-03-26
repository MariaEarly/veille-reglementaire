#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$ROOT_DIR/veille_aggregator_mvp/veille_aggregator_mvp"
PID_FILE="$APP_DIR/.veille_ui.pid"

if [[ ! -f "$PID_FILE" ]]; then
  osascript -e 'display notification "Aucun serveur local enregistre." with title "Veille Aggregator MVP"'
  exit 0
fi

SERVER_PID="$(cat "$PID_FILE" 2>/dev/null || true)"

if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
  kill "$SERVER_PID"
fi

rm -f "$PID_FILE"
osascript -e 'display notification "Serveur local arrete." with title "Veille Aggregator MVP"'
