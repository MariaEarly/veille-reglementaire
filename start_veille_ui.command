#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$ROOT_DIR/veille_aggregator_mvp/veille_aggregator_mvp"
VENV_DIR="$APP_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
UVICORN_BIN="$VENV_DIR/bin/uvicorn"
PID_FILE="$APP_DIR/.veille_ui.pid"
LOG_FILE="$APP_DIR/.veille_ui.log"
URL="http://127.0.0.1:8000/"

if [[ ! -d "$APP_DIR" ]]; then
  osascript -e 'display alert "Projet introuvable" message "Le dossier du MVP est introuvable." as critical'
  exit 1
fi

cd "$APP_DIR"

# Always clear Python bytecode cache to ensure fresh code is served
find "$APP_DIR" -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "$APP_DIR" -name '*.pyc' -delete 2>/dev/null || true

if [[ ! -x "$PYTHON_BIN" ]]; then
  python3 -m venv "$VENV_DIR"
fi

if [[ ! -x "$UVICORN_BIN" ]]; then
  "$PIP_BIN" install -r requirements.txt
fi

if [[ -f "$PID_FILE" ]]; then
  EXISTING_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${EXISTING_PID:-}" ]] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    open "$URL"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

# Remove corrupted DB and let SQLAlchemy recreate it on startup
DB_FILE="$APP_DIR/veille.db"
if [[ -f "$DB_FILE" ]]; then
  # Check if DB is corrupt (sqlite3 integrity check)
  if ! sqlite3 "$DB_FILE" "PRAGMA integrity_check;" >/dev/null 2>&1; then
    echo "Database appears corrupted, backing up and recreating..."
    mv "$DB_FILE" "$DB_FILE.bak.$(date +%s)" 2>/dev/null || true
    rm -f "$DB_FILE-wal" "$DB_FILE-shm" 2>/dev/null || true
  fi
fi

nohup "$UVICORN_BIN" app.main:app --host 127.0.0.1 --port 8000 --reload >"$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

for _ in {1..30}; do
  if curl -sf "$URL" >/dev/null 2>&1; then
    # Auto-seed sources on first launch (idempotent)
    curl -sf -X POST "${URL}sources/seed" >/dev/null 2>&1 || true
    open "$URL"
    exit 0
  fi
  sleep 1
done

rm -f "$PID_FILE"
osascript -e 'display alert "Demarrage echoue" message "Le serveur n a pas repondu. Consulte .veille_ui.log dans le dossier du projet." as critical'
exit 1
