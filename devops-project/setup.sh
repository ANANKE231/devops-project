#!/usr/bin/env bash
# ============================================================
#  setup.sh — Single-command environment bootstrap
#  Usage: bash setup.sh
# ============================================================
set -euo pipefail

log() { echo -e "\033[1;32m[SETUP]\033[0m $*"; }
err() { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; exit 1; }

log "DevOps Demo — Environment Setup"
log "================================"

# ── Check Python ──────────────────────────────────────────
command -v python3 &>/dev/null || err "python3 is required"
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Python $PY_VER detected"

# ── Install pip deps ──────────────────────────────────────
log "Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

# ── Create directories ────────────────────────────────────
log "Creating directory structure..."
mkdir -p /opt/devops-demo/{blue,green,releases}
mkdir -p /var/log/devops-demo 2>/dev/null || mkdir -p ./logs

# ── Copy app files ────────────────────────────────────────
log "Staging app files..."
cp -r app/. /opt/devops-demo/blue/
cp -r app/. /opt/devops-demo/green/
echo "blue" > /opt/devops-demo/active_slot

# ── Copy scripts ──────────────────────────────────────────
cp scripts/*.sh /opt/devops-demo/
chmod +x /opt/devops-demo/*.sh

# ── Run tests ─────────────────────────────────────────────
log "Running test suite..."
pytest tests/ -q && log "All tests passed ✅" || err "Tests failed"

log ""
log "✅  Setup complete!"
log "   Start app:    APP_ENV=production PORT=5001 python3 app/app.py"
log "   Deploy:       bash scripts/deploy.sh v1.0"
log "   Health check: bash scripts/health_check.sh"
log "   Rollback:     bash scripts/rollback.sh"
log ""
log "   Or use Ansible: ansible-playbook -i ansible/inventory.ini ansible/setup.yml"
