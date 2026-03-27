#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"

cleanup() {
  if [[ -n "${API_PID:-}" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null || true
  fi
  if [[ -n "${WEB_PID:-}" ]] && kill -0 "$WEB_PID" 2>/dev/null; then
    kill "$WEB_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "[dev] Iniciando API Flask en http://localhost:${API_PORT}"
PYTHONPATH="$ROOT_DIR/src" flask --app api_server run --port "$API_PORT" &
API_PID=$!

echo "[dev] Iniciando frontend estatico en http://localhost:${WEB_PORT}"
python3 -m http.server "$WEB_PORT" --directory "$ROOT_DIR/frontend" &
WEB_PID=$!

echo "[dev] Listo. Presiona Ctrl+C para detener ambos servicios."
wait "$API_PID" "$WEB_PID"
