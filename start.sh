#!/usr/bin/env bash
# Trinetra Enterprise SIEM - Quick Launcher (Linux/macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo " ========================================"
echo "    TRINETRA ENTERPRISE SIEM - Launcher"
echo " ========================================"
echo ""

# Check dependencies
command -v python3 >/dev/null 2>&1 && PYTHON=python3 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || { echo "[ERROR] Python not found"; exit 1; }
echo "[OK] Python found"

command -v node >/dev/null 2>&1 || { echo "[ERROR] Node.js not found"; exit 1; }
echo "[OK] Node.js found"

if command -v ollama >/dev/null 2>&1; then
    echo "[OK] Ollama found"
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "[*] Starting Ollama..."
        ollama serve &
    fi
else
    echo "[!] Ollama not found - AI features offline"
fi

# Kill stale processes
kill $(lsof -ti:8000) 2>/dev/null || true
kill $(lsof -ti:5173) 2>/dev/null || true

# Start Backend
echo ""
echo "[*] Starting Backend (port 8000)..."
$PYTHON run_backend.py &
BACKEND_PID=$!
sleep 3

# Check backend
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "[OK] Backend running on http://localhost:8000"
else
    echo "[ERROR] Backend failed to start"
    exit 1
fi

# Start Frontend
echo "[*] Starting Frontend (port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

sleep 4

echo ""
echo " ========================================"
echo "    TRINETRA IS STARTING UP"
echo " ========================================"
echo ""
echo "    Frontend: http://localhost:5173"
echo "    Backend:  http://localhost:8000"
echo "    API Docs: http://localhost:8000/docs"
echo "    Health:   http://localhost:8000/health"
echo ""
echo "    First time? Register at http://localhost:5173/register"
echo ""

# Open browser
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:5173
elif command -v open >/dev/null 2>&1; then
    open http://localhost:5173
fi

# Trap to clean up on exit
cleanup() {
    echo ""
    echo "[*] Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "[OK] All servers stopped"
}
trap cleanup EXIT INT TERM

echo "Press Ctrl+C to shut down all servers."
wait
