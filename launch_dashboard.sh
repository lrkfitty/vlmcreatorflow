#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# VLM Mission Control — Launch Script
# Port: 8502 (separate from CreateFlow main on 8501)
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv313"

echo ""
echo "  ⚡ VLM MISSION CONTROL"
echo "  ───────────────────────────────────────"
echo "  Port : 8502"
echo "  Root : $SCRIPT_DIR"
echo ""

# Activate venv
if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
    echo "  ✓ venv313 activated"
else
    echo "  ⚠  venv313 not found at $VENV"
    echo "     Trying system python..."
fi

# Ensure .tmp dir exists
mkdir -p "$SCRIPT_DIR/.tmp"

# Check streamlit is available
if ! command -v streamlit &>/dev/null; then
    echo ""
    echo "  ✗ streamlit not found — installing..."
    pip install streamlit --quiet
fi

echo "  ✓ Launching dashboard on http://localhost:8502"
echo ""

cd "$SCRIPT_DIR"
streamlit run dashboard.py \
    --server.port 8502 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.base dark \
    --theme.backgroundColor "#0a0a0f" \
    --theme.secondaryBackgroundColor "#12121a" \
    --theme.primaryColor "#00ffff" \
    --theme.textColor "#c8d6e5"
