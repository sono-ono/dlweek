import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread
import shutil
import signal
import flask

def check_npm_installed():
    """Check if npm is installed and available in the PATH."""
    npm_path = shutil.which('npm')
    if not npm_path:
        print("ERROR: npm is not installed or not in your PATH.")
        print("Please install Node.js and npm from https://nodejs.org/")
        print("After installation, restart this script.")
        return False
    return True

def run_backend():
    print("Starting Flask backend...")
    try:
        if sys.platform.startswith('win'):
            return subprocess.Popen([r".\.venv\Scripts\python.exe", "app.py"], 
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            return subprocess.Popen(["./.venv/bin/python", "app.py"])
    except Exception as e:
        print(f"Error starting backend: {str(e)}")
        return None

def run_frontend():
    print("Starting React frontend...")
    # Store the current directory
    original_dir = os.getcwd()
    try:
        # Change to the frontend directory
        frontend_dir = os.path.join(original_dir, "frontend")
        if not os.path.exists(frontend_dir):
            print(f"Error: Frontend directory not found at {frontend_dir}")
            return None
            
        os.chdir(frontend_dir)
        
        # Check if package.json exists
        if not os.path.exists("package.json"):
            print("Error: package.json not found in frontend directory")
            return None
            
        # Get the full path to npm
        npm_path = shutil.which('npm')
        if not npm_path:
            print("Error: npm not found in PATH")
            return None
            
        print(f"Using npm from: {npm_path}")
        print(f"Current directory: {os.getcwd()}")
        
        # Run npm start in the frontend directory
        if sys.platform.startswith('win'):
            return subprocess.Popen([npm_path, "start"], 
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            return subprocess.Popen([npm_path, "start"])
    except Exception as e:
        print(f"Error starting frontend: {str(e)}")
        return None
    finally:
        # Change back to the original directory
        os.chdir(original_dir)

def open_browser():
    print("Waiting for servers to start...")
    time.sleep(10)  # Give servers more time to start
    print("Opening application in browser...")
    try:
        webbrowser.open("http://localhost:3000")
    except Exception as e:
        print(f"Error opening browser: {str(e)}")
        print("Please manually open http://localhost:3000 in your browser")

if __name__ == "__main__":
    # Check if npm is installed
    if not check_npm_installed():
        sys.exit(1)
        
    # Check if frontend/node_modules exists
    if not os.path.exists("frontend/node_modules"):
        print("Installing frontend dependencies...")
        original_dir = os.getcwd()
        try:
            os.chdir("frontend")
            subprocess.call(["npm", "install"], shell=True)
        finally:
            os.chdir(original_dir)

    # Start backend and frontend
    backend_process = run_backend()
    time.sleep(2)  # Give backend time to start before starting frontend
    frontend_process = run_frontend()
    
    # Open browser in a separate thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("Application started! Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        # Terminate processes
        if backend_process:
            if sys.platform.startswith('win'):
                backend_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                backend_process.terminate()
        if frontend_process:
            if sys.platform.startswith('win'):
                frontend_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                frontend_process.terminate()
        sys.exit(0) 