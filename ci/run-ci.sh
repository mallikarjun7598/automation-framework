#!/usr/bin/env bash
#
# run-ci.sh — a LOCAL CI/CD pipeline mock-up.
#
# It runs the same stages a hosted CI system (GitHub Actions, Jenkins, etc.)
# would run, in order, and stops on the first failure. This lets you "feel" the
# pipeline on your own machine before pushing.
#
# Stages:  setup -> lint -> build/boot app -> web tests -> mobile tests -> report
#
# Usage:
#   ./ci/run-ci.sh            # full pipeline (mobile stage skips without a device)
#   ./ci/run-ci.sh --mobile   # also attempt real mobile tests (needs Appium)
#
set -euo pipefail

# --- resolve paths (script is in ci/, project root is one level up) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

VENV_PY="$ROOT/.venv/bin/python"
RUN_MOBILE=0
[[ "${1:-}" == "--mobile" ]] && RUN_MOBILE=1

# --- pretty stage headers ---
stage() { printf "\n\033[1;36m==> %s\033[0m\n" "$1"; }
ok()    { printf "\033[1;32m[OK]\033[0m %s\n" "$1"; }
fail()  { printf "\033[1;31m[FAIL]\033[0m %s\n" "$1"; exit 1; }

# ------------------------------------------------------------------ setup
stage "Stage 1/6: Setup — verify virtual environment"
if [[ ! -x "$VENV_PY" ]]; then
  fail "No virtualenv at .venv. Run: make install"
fi
ok "virtualenv present ($($VENV_PY --version))"

# ------------------------------------------------------------------ lint
stage "Stage 2/6: Lint — ruff static analysis"
"$VENV_PY" -m ruff check app tests || fail "Lint failed"
ok "lint clean"

# ------------------------------------------------------------------ build/boot
stage "Stage 3/6: Build — boot the app and health-check it"
PORT=5001
PORT=$PORT HOST=127.0.0.1 "$VENV_PY" -m app.server >/tmp/mini-retail-ci.log 2>&1 &
APP_PID=$!
# Ensure the app is torn down no matter how the script exits.
trap '[[ -n "${APP_PID:-}" ]] && kill "$APP_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then break; fi
  sleep 0.3
done
curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 || fail "App did not become healthy"
ok "app healthy on port $PORT"
export BASE_URL="http://127.0.0.1:$PORT"

# ------------------------------------------------------------------ web tests
stage "Stage 4/6: Web tests — Playwright"
"$VENV_PY" -m pytest tests/web -m web --browser chromium \
  --html=reports/web-report.html --self-contained-html \
  || fail "Web tests failed"
ok "web tests passed"

# ------------------------------------------------------------------ mobile tests
stage "Stage 5/6: Mobile tests — Appium"
if [[ "$RUN_MOBILE" == "1" ]]; then
  "$VENV_PY" -m pytest tests/mobile -m mobile --appium \
    --html=reports/mobile-report.html --self-contained-html \
    || fail "Mobile tests failed"
  ok "mobile tests passed"
else
  "$VENV_PY" -m pytest tests/mobile -m mobile \
    --html=reports/mobile-report.html --self-contained-html
  ok "mobile tests ran (skipped — no device; pass --mobile to run for real)"
fi

# ------------------------------------------------------------------ report
stage "Stage 6/6: Report"
ok "Reports written to reports/web-report.html and reports/mobile-report.html"

printf "\n\033[1;32mPIPELINE SUCCEEDED\033[0m\n"
