#!/usr/bin/env bash
# ALCIDAS Installer
# Usage:
#   curl -fsSL https://install.alcidas.com | bash -s -- --license-key=YOUR_KEY
#   bash install.sh --license-key=YOUR_KEY
#   bash install.sh --dev --license-key=TEST_KEY   # skip phone-home

set -euo pipefail

# ── Constants ────────────────────────────────────────────────────────────────
ALCIDAS_VERSION="${ALCIDAS_VERSION:-latest}"
ALCIDAS_REPO="https://github.com/Altus-Cere/alcidas.git"
ALCIDAS_AUTH_URL="${ALCIDAS_AUTH_URL:-https://auth.alcidas.com/v1/license/validate}"
ALCIDAS_INSTALL_DIR="${ALCIDAS_INSTALL_DIR:-/opt/alcidas}"
ALCIDAS_SERVICE_NAME="alcidas-gateway"
PYTHON_MIN="3.11"

# ── Color output ─────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[alcidas]${NC} $*"; }
warn()    { echo -e "${YELLOW}[alcidas]${NC} $*"; }
error()   { echo -e "${RED}[alcidas] ERROR:${NC} $*" >&2; exit 1; }

# ── Arg parsing ──────────────────────────────────────────────────────────────
LICENSE_KEY=""
DEV_MODE=false
UNINSTALL=false

for arg in "$@"; do
  case "$arg" in
    --license-key=*) LICENSE_KEY="${arg#*=}" ;;
    --license-key)   shift; LICENSE_KEY="${1:-}" ;;
    --dev)           DEV_MODE=true ;;
    --uninstall)     UNINSTALL=true ;;
    --version=*)     ALCIDAS_VERSION="${arg#*=}" ;;
    --help|-h)
      echo "Usage: install.sh [--license-key=KEY] [--dev] [--uninstall] [--version=X]"
      exit 0 ;;
    *) warn "Unknown argument: $arg" ;;
  esac
done

# ── Uninstall path ───────────────────────────────────────────────────────────
if [[ "$UNINSTALL" == true ]]; then
  info "Stopping and removing ALCIDAS..."
  if command -v systemctl &>/dev/null; then
    systemctl stop "$ALCIDAS_SERVICE_NAME" 2>/dev/null || true
    systemctl disable "$ALCIDAS_SERVICE_NAME" 2>/dev/null || true
    rm -f "/etc/systemd/system/${ALCIDAS_SERVICE_NAME}.service"
    systemctl daemon-reload
  fi
  rm -rf "$ALCIDAS_INSTALL_DIR"
  info "ALCIDAS uninstalled."
  exit 0
fi

# ── Require license key ──────────────────────────────────────────────────────
if [[ -z "$LICENSE_KEY" ]]; then
  error "License key required. Get yours at https://alcidas.com\n       Run: install.sh --license-key=YOUR_KEY"
fi

echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║   ALCIDAS Gateway Installer       ║"
echo "  ║   Altus Cere LLC                  ║"
echo "  ╚═══════════════════════════════════╝"
echo ""

# ── License validation ───────────────────────────────────────────────────────
validate_license() {
  local key="$1"

  if [[ "$DEV_MODE" == true ]]; then
    warn "Dev mode: skipping license validation."
    echo '{"valid":true,"customer_id":"dev","plan":"dev","display_name":"Dev Instance"}'
    return 0
  fi

  info "Validating license key..."

  local response http_code body
  response=$(curl -s -w "\n%{http_code}" \
    -X POST "$ALCIDAS_AUTH_URL" \
    -H "Content-Type: application/json" \
    -d "{\"license_key\": \"${key}\", \"installer_version\": \"${ALCIDAS_VERSION}\"}" \
    --max-time 15 2>&1) || error "Could not reach license server. Check your internet connection."

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)

  if [[ "$http_code" == "200" ]]; then
    local valid
    valid=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('valid','false'))" 2>/dev/null || echo "false")
    if [[ "$valid" == "True" || "$valid" == "true" ]]; then
      info "License valid."
      echo "$body"
      return 0
    fi
  elif [[ "$http_code" == "402" || "$http_code" == "403" ]]; then
    error "License key invalid or subscription inactive.\n       Manage your subscription at https://alcidas.com/billing"
  elif [[ "$http_code" == "429" ]]; then
    error "Too many validation attempts. Wait a few minutes and try again."
  fi

  error "License validation failed (HTTP $http_code). Contact support@alcidas.com"
}

LICENSE_DATA=$(validate_license "$LICENSE_KEY")

# ── System checks ────────────────────────────────────────────────────────────
info "Checking system requirements..."

OS="$(uname -s)"
case "$OS" in
  Linux)  : ;;
  Darwin) : ;;
  *)      error "Unsupported OS: $OS. ALCIDAS requires Linux or macOS." ;;
esac

# Python 3.11+
PYTHON=""
for cmd in python3.12 python3.11 python3; do
  if command -v "$cmd" &>/dev/null; then
    ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
    major="${ver%%.*}"; minor="${ver##*.}"
    if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
      PYTHON="$cmd"; break
    fi
  fi
done
[[ -z "$PYTHON" ]] && error "Python ${PYTHON_MIN}+ not found. Install it and re-run."
info "Using Python: $PYTHON ($($PYTHON --version))"

# git
command -v git &>/dev/null || error "git not found. Install git and re-run."

# curl
command -v curl &>/dev/null || error "curl not found."

# ── Clone / update ───────────────────────────────────────────────────────────
if [[ -d "$ALCIDAS_INSTALL_DIR/.git" ]]; then
  info "Updating existing installation at $ALCIDAS_INSTALL_DIR..."
  git -C "$ALCIDAS_INSTALL_DIR" fetch --tags origin
  if [[ "$ALCIDAS_VERSION" == "latest" ]]; then
    git -C "$ALCIDAS_INSTALL_DIR" checkout main
    git -C "$ALCIDAS_INSTALL_DIR" pull --ff-only origin main
  else
    git -C "$ALCIDAS_INSTALL_DIR" checkout "$ALCIDAS_VERSION"
  fi
else
  info "Cloning ALCIDAS to $ALCIDAS_INSTALL_DIR..."
  mkdir -p "$(dirname "$ALCIDAS_INSTALL_DIR")"
  if [[ "$ALCIDAS_VERSION" == "latest" ]]; then
    git clone "$ALCIDAS_REPO" "$ALCIDAS_INSTALL_DIR"
  else
    git clone --branch "$ALCIDAS_VERSION" "$ALCIDAS_REPO" "$ALCIDAS_INSTALL_DIR"
  fi
fi

# ── Python venv + dependencies ───────────────────────────────────────────────
info "Setting up Python environment..."
VENV="$ALCIDAS_INSTALL_DIR/.venv"
[[ -d "$VENV" ]] || "$PYTHON" -m venv "$VENV"

info "Installing dependencies (this takes ~2 minutes on first run)..."
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -e "$ALCIDAS_INSTALL_DIR/upstream/hermes[messaging,cron,honcho]"

# ── Write .env ───────────────────────────────────────────────────────────────
ENV_FILE="$ALCIDAS_INSTALL_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  info "Creating .env — fill in TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY to start."
  cat > "$ENV_FILE" <<ENV
# ALCIDAS runtime configuration
# Generated by installer on $(date -u +"%Y-%m-%d")

ALCIDAS_LICENSE_KEY=${LICENSE_KEY}

# Telegram bot token (from @BotFather)
TELEGRAM_BOT_TOKEN=

# Owner's Telegram chat ID (send /start to your bot, then check getUpdates)
ALCIDAS_HOME_CHAT_ID=

# Model API keys
ANTHROPIC_API_KEY=
# OPENAI_API_KEY=   # optional — used for GPT-4o fallback

# Auth server (override for staging)
# ALCIDAS_AUTH_URL=https://auth.alcidas.com/v1/license/validate
ENV
else
  warn ".env already exists — skipping. Update ALCIDAS_LICENSE_KEY if you renewed."
  # Always refresh the license key in case it was renewed
  if grep -q "ALCIDAS_LICENSE_KEY=" "$ENV_FILE"; then
    sed -i "s|ALCIDAS_LICENSE_KEY=.*|ALCIDAS_LICENSE_KEY=${LICENSE_KEY}|" "$ENV_FILE"
  else
    echo "ALCIDAS_LICENSE_KEY=${LICENSE_KEY}" >> "$ENV_FILE"
  fi
fi

# ── Systemd service (Linux only) ─────────────────────────────────────────────
if [[ "$OS" == "Linux" ]] && command -v systemctl &>/dev/null; then
  PYTHON_BIN="$VENV/bin/python"
  SERVICE_FILE="/etc/systemd/system/${ALCIDAS_SERVICE_NAME}.service"

  info "Installing systemd service: $ALCIDAS_SERVICE_NAME"
  cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=ALCIDAS Gateway (Altus Cere)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${ALCIDAS_INSTALL_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=${PYTHON_BIN} -m alcidas.core.main
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=alcidas

[Install]
WantedBy=multi-user.target
SERVICE

  systemctl daemon-reload
  systemctl enable "$ALCIDAS_SERVICE_NAME"
  warn "Service installed but NOT started — fill in .env first, then:"
  warn "  sudo systemctl start $ALCIDAS_SERVICE_NAME"
  warn "  sudo journalctl -u $ALCIDAS_SERVICE_NAME -f"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
info "Installation complete."
echo ""
echo "  Next steps:"
echo "  1. Edit ${ENV_FILE}"
echo "     → Set TELEGRAM_BOT_TOKEN (from @BotFather)"
echo "     → Set ALCIDAS_HOME_CHAT_ID (your Telegram chat ID)"
echo "     → Set ANTHROPIC_API_KEY"
echo ""
if [[ "$OS" == "Linux" ]] && command -v systemctl &>/dev/null; then
  echo "  2. sudo systemctl start $ALCIDAS_SERVICE_NAME"
  echo "  3. sudo journalctl -u $ALCIDAS_SERVICE_NAME -f"
else
  echo "  2. cd ${ALCIDAS_INSTALL_DIR}"
  echo "     .venv/bin/python -m alcidas.core.main"
fi
echo ""
