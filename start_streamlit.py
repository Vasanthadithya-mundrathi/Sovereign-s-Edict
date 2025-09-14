"""
Startup script for Sovereign's Edict with Streamlit as the default frontend
"""
import subprocess
import sys
import os
import time
import threading

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend server...")
    backend_process = subprocess.Popen([
        sys.executable, 
        os.path.join("backend", "main.py")
    ])
    return backend_process

def start_streamlit():
    """Start the Streamlit frontend"""
    print("Starting Streamlit frontend...")
    streamlit_process = subprocess.Popen([
        "streamlit", 
        "run", 
        "streamlit_app.py",
        "--server.port", "8503",  # Use port 8503 instead of 8502
        "--server.address", "localhost"
    ])
    return streamlit_process

def main():
    """Main function to start both backend and frontend"""
    print("🏛️  Starting Sovereign's Edict with Streamlit as default frontend")
    print("=" * 60)
    
    # Start backend
    try:
        backend_process = start_backend()
        print("✅ Backend server started successfully")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return
    
    # Wait a moment for backend to initialize
    time.sleep(3)
    
    # Start Streamlit frontend
    try:
        streamlit_process = start_streamlit()
        print("✅ Streamlit frontend started successfully")
    except Exception as e:
        print(f"❌ Failed to start Streamlit frontend: {e}")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎉 Sovereign's Edict is now running!")
    print("   Backend API:    http://localhost:8001")
    print("   Streamlit UI:   http://localhost:8503")  # Updated port
    print("=" * 60)
    print("Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Wait for both processes
        backend_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        streamlit_process.terminate()
        print("✅ Servers stopped successfully")

if __name__ == "__main__":
    main()