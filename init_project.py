#!/usr/bin/env python3
"""
Project initialization script for Sovereign's Edict
"""
import os
import subprocess
import sys

def check_prerequisites():
    """Check if required tools are installed"""
    prerequisites = {
        "Python": "python3 --version",
        "Node.js": "node --version",
        "npm": "npm --version",
        "Docker": "docker --version",
        "Docker Compose": "docker-compose --version"
    }
    
    print("Checking prerequisites...")
    missing = []
    
    for name, command in prerequisites.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {name}: {result.stdout.strip()}")
            else:
                print(f"✗ {name}: Not found")
                missing.append(name)
        except FileNotFoundError:
            print(f"✗ {name}: Not found")
            missing.append(name)
    
    if missing:
        print(f"\nMissing prerequisites: {', '.join(missing)}")
        print("Please install the missing tools before proceeding.")
        return False
    
    return True

def install_dependencies():
    """Install project dependencies"""
    print("\nInstalling backend dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Backend dependencies installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install backend dependencies")
        return False
    
    print("\nInstalling frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✓ Frontend dependencies installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install frontend dependencies")
        return False
    
    return True

def build_docker_images():
    """Build Docker images"""
    print("\nBuilding Docker images...")
    try:
        subprocess.run(["docker", "build", "-t", "sovereigns-edict-backend", "."], check=True)
        print("✓ Backend Docker image built")
        
        subprocess.run(["docker", "build", "-t", "sovereigns-edict-frontend", "-f", "Dockerfile.frontend", "."], 
                      cwd="frontend", check=True)
        print("✓ Frontend Docker image built")
    except subprocess.CalledProcessError:
        print("✗ Failed to build Docker images")
        return False
    
    return True

def main():
    """Main initialization function"""
    print("Sovereign's Edict - Project Initialization")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Build Docker images
    if not build_docker_images():
        sys.exit(1)
    
    print("\n✓ Project initialization complete!")
    print("\nTo run the application:")
    print("  Option 1 (Docker): docker-compose up")
    print("  Option 2 (Manual): ")
    print("    - Terminal 1: cd backend && python main.py")
    print("    - Terminal 2: cd frontend && npm start")
    
    print("\nTo run tests:")
    print("  cd backend && python -m pytest tests/")

if __name__ == "__main__":
    main()