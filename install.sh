#!/usr/bin/env bash
set -e

KEYTRACE_VERSION="1.0.0"
INSTALL_DIR="$HOME/.keytrace"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()     { echo -e "${CYAN}[KeyTrace]${NC} $1"; }
ok()      { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()     { echo -e "${RED}[ERR]${NC} $1"; exit 1; }
section() { echo -e "\n${BOLD}── $1${NC}"; }

echo ""
echo -e "${CYAN}${BOLD}  KEYTRACE v${KEYTRACE_VERSION} — Installer${NC}"
echo ""
echo "  This installer will:"
echo "  - Check your Python version"
echo "  - Install PyQt6"
echo "  - Install KeyTrace to ~/.keytrace"
echo "  - Create a desktop shortcut"
echo ""
read -p "  Press Enter to continue or Ctrl+C to cancel..."

section "Step 1 — Checking Python"
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            PYTHON="$cmd"
            ok "Found Python $VERSION"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    err "Python 3.8+ not found. Install it first: sudo apt install python3"
fi

section "Step 2 — Installing dependencies"
log "Installing PyQt6..."
if "$PYTHON" -m pip install PyQt6 --break-system-packages -q 2>/dev/null || \
   "$PYTHON" -m pip install PyQt6 -q 2>/dev/null; then
    ok "PyQt6 installed"
else
    sudo apt install -y python3-pyqt6 && ok "PyQt6 installed via apt"
fi

if command -v tshark &>/dev/null || [ -f "/usr/bin/tshark" ]; then
    ok "tshark found"
else
    warn "tshark not found. Install it: sudo apt install tshark"
fi

section "Step 3 — Installing KeyTrace"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/core/commands"
mkdir -p "$INSTALL_DIR/assets"

FILES=(gui.py main.py browser_launcher.py start_keytrace.py decryptor.py)
for file in "${FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
        ok "Copied $file"
    else
        warn "Missing: $file"
    fi
done

if [ -d "$SCRIPT_DIR/core" ]; then
    cp -r "$SCRIPT_DIR/core/." "$INSTALL_DIR/core/"
    ok "Copied core/ package"
fi

if [ -d "$SCRIPT_DIR/assets" ]; then
    cp -r "$SCRIPT_DIR/assets/." "$INSTALL_DIR/assets/"
    ok "Copied assets/"
fi

section "Step 4 — Creating launcher"
LAUNCHER="$INSTALL_DIR/keytrace"
cat > "$LAUNCHER" << EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec $PYTHON "$INSTALL_DIR/gui.py" "\$@"
EOF
chmod +x "$LAUNCHER"
sudo ln -sf "$LAUNCHER" /usr/local/bin/keytrace 2>/dev/null && ok "Added 'keytrace' command to PATH"

section "Step 5 — Desktop shortcut"
DESKTOP_FILE="$HOME/Desktop/KeyTrace.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=KeyTrace
Comment=TLS Traffic Decryption Tool
Exec=$PYTHON $INSTALL_DIR/gui.py
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Categories=Network;Security;
StartupNotify=true
EOF
chmod +x "$DESKTOP_FILE"
ok "Desktop shortcut created"

echo ""
echo -e "${GREEN}${BOLD}─────────────────────────────────────────${NC}"
echo -e "${GREEN}${BOLD}  KeyTrace v${KEYTRACE_VERSION} installed successfully!${NC}"
echo -e "${GREEN}${BOLD}─────────────────────────────────────────${NC}"
echo ""
echo "  Launch options:"
echo "  - Double-click KeyTrace on your Desktop"
echo "  - Or run: keytrace"
echo ""
