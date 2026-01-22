import subprocess
import time
import sys
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
LOG_FILE = "logs/hopon.log"
APP_COMMAND = [sys.executable, "-m", "streamlit", "run", "app.py"]

def follow(file):
    """Generator that yields new lines from a file."""
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Start Streamlit in the background
    print(f"[INFO] Launching HopOn: {' '.join(APP_COMMAND)}")
    process = subprocess.Popen(APP_COMMAND)

    try:
        # Wait for the app to start
        time.sleep(2)
        
        # Check if log file exists and has content
        if not os.path.exists(LOG_FILE):
            print(f"[WARN] {LOG_FILE} not found. Creating empty file...")
            with open(LOG_FILE, 'w') as f:
                f.write("")
            print("[ERR] No logs detected! Make sure app.py has logging configured:")
            print("   logger.add('logs/hopon.log', ...)")
        else:
            file_size = os.path.getsize(LOG_FILE)
            if file_size == 0:
                print(f"[WARN] {LOG_FILE} is empty. App may not be logging yet...")
            else:
                print(f"[OK] Log file detected ({file_size} bytes)")

        print(f"[INFO] Watching logs: {LOG_FILE}\n" + "-"*40)
        
        with open(LOG_FILE, "r") as logfile:
            # Follow new lines
            for line in follow(logfile):
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # Check if process is still alive
                if process.poll() is not None:
                    break

    except KeyboardInterrupt:
        print("\n[STOP] Stopping HopOn...")
        
        # Log shutdown BEFORE killing the process
        logger.remove()
        logger.add(LOG_FILE, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")
        logger.critical("APPLICATION SHUTDOWN (User Initiated)")
        
        # Properly terminate the process
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("[WARN] Process didn't stop gracefully, forcing kill...")
            process.kill()
            process.wait()
        
        print("[OK] HopOn stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()