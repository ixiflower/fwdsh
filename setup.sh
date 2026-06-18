#!/bin/bash
REPO_URL="https://github.com/ixiflower/fwdsh.git"
INSTALL_DIR="$HOME/.fwdsh"

if [ -d "$INSTALL_DIR" ]; then
    echo "[*] Updating existing installation in $INSTALL_DIR"
    cd "$INSTALL_DIR" && git pull
else
    echo "[*] Cloning fwdsh into $INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo "[*] Starting rce_server.py in background..."
cd "$INSTALL_DIR"
nohup python3 rce_server.py > "$HOME/.fwdsh.log" 2>&1 &
PID=$!
echo $PID > "$HOME/.fwdsh.pid"
echo "[*] RCE server started (PID: $PID) on port 54321"
