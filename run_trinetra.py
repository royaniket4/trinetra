import os
import sys
import platform
import subprocess
import time
import signal
import atexit

# List to keep track of running processes
processes = []

def cleanup():
    """Ensure all child processes are terminated when the script exits."""
    print("\n[Trinetra] Shutting down all services gracefully...")
    for p in processes:
        try:
            if p.poll() is None:  # If process is still running
                p.terminate()
                p.wait(timeout=3)
        except Exception:
            try:
                p.kill() # Force kill if terminate fails
            except Exception:
                pass
    print("[Trinetra] All services stopped.")

# Register the cleanup function to run on exit
atexit.register(cleanup)

def signal_handler(sig, frame):
    """Handle Ctrl+C to trigger cleanup."""
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("="*50)
    print("   Starting Trinetra - AI Cyber Defense Center   ")
    print("="*50)

    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    ollama_cmd = "ollama" # Usually 'ollama' works on all OS if in PATH

    # 1. Start Ollama
    print("\n[1/3] Starting Ollama AI Service...")
    try:
        # Check if ollama is installed
        subprocess.run([ollama_cmd, "--version"], capture_output=True, check=True)
        
        # Start ollama serve in background
        # We redirect output to DEVNULL to avoid cluttering the terminal
        p_ollama = subprocess.Popen(
            [ollama_cmd, "serve"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        processes.append(p_ollama)
        print("✅ Ollama started (or already running).")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  WARNING: Ollama not found in PATH or not installed.")
        print("   AI features might not work unless Ollama is running.")

    # Give Ollama a second to initialize
    time.sleep(2)

    # 2. Start Backend
    print("\n[2/3] Starting Python Backend...")
    backend_env = os.environ.copy()
    # Add current directory to PYTHONPATH so backend modules can be found
    backend_env["PYTHONPATH"] = os.path.abspath(".")
    
    try:
        p_backend = subprocess.Popen(
            [sys.executable, "backend/main.py"], 
            env=backend_env
        )
        processes.append(p_backend)
        print("✅ Backend started successfully.")
    except Exception as e:
        print(f"❌ Failed to start Backend: {e}")

    # Give backend a second to bind to port
    time.sleep(2)

    # 3. Start Frontend
    print("\n[3/3] Starting React Frontend...")
    frontend_dir = os.path.join(os.path.abspath("."), "frontend")
    
    try:
        p_frontend = subprocess.Popen(
            [npm_cmd, "run", "dev"], 
            cwd=frontend_dir
        )
        processes.append(p_frontend)
        print("✅ Frontend started successfully.")
    except Exception as e:
        print(f"❌ Failed to start Frontend: {e}")

    print("\n" + "="*50)
    print("🚀 TRINETRA IS NOW RUNNING!")
    print("👉 Frontend UI : http://localhost:5173")
    print("👉 Backend API : http://localhost:8000")
    print("🛑 Press Ctrl+C to stop all services.")
    print("="*50 + "\n")

    # Keep main thread alive waiting for processes
    try:
        # Wait for any process to complete (usually they shouldn't unless they crash)
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        # This will trigger the signal_handler and cleanup
        sys.exit(0)

if __name__ == "__main__":
    main()
