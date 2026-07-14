#!/usr/bin/env python3
"""
Service Manager for AI DevOps Incident Commander
Starts/Stops all services with a single command

Usage:
    python manage-services.py start    # Start all services
    python manage-services.py stop     # Stop all services
    python manage-services.py status   # Check service status
    python manage-services.py restart  # Restart all services
"""

import os
import sys
import subprocess
import time
import json
import signal
import shutil
from pathlib import Path
from typing import Dict, Optional

# Fix encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Configuration
PROJECT_ROOT = Path(__file__).parent
SERVICES = {
    "backend": {
        "name": "Backend (Spring Boot)",
        "port": 8080,
        "directory": PROJECT_ROOT / "backend",
        "start_cmd": ["mvn", "spring-boot:run"],
        "health_url": "http://localhost:8080/actuator/health"
    },
    "frontend": {
        "name": "Frontend (React)",
        "port": 5173,
        "directory": PROJECT_ROOT / "frontend",
        "start_cmd": ["npm", "run", "dev"],
        "health_url": "http://localhost:5173"
    },
    "ai-service": {
        "name": "AI Service (Python/FastAPI)",
        "port": 8002,
        "directory": PROJECT_ROOT / "ai-service",
        "start_cmd": ["python", "src/main.py"],
        "health_url": "http://localhost:8002/health"
    },
    "simulator": {
        "name": "Simulator (Python/FastAPI)",
        "port": 8001,
        "directory": PROJECT_ROOT / "simulator",
        "start_cmd": ["python", "src/main.py"],
        "health_url": "http://localhost:8001/health"
    }
}

PIDS_FILE = PROJECT_ROOT / ".service_pids.json"


def find_command(command: str) -> Optional[str]:
    """Find a command in system PATH."""
    return shutil.which(command)


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            return f":{port}" in result.stdout
        else:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True
            )
            return result.returncode == 0
    except Exception:
        return False


def kill_process_on_port(port: int) -> bool:
    """Kill process using a specific port."""
    try:
        if sys.platform == "win32":
            # Find PID using the port
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True
                        )
                        print(f"   Killed process {pid} on port {port}")
                        return True
        else:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip()
                os.kill(int(pid), signal.SIGKILL)
                print(f"   Killed process {pid} on port {port}")
                return True
    except Exception as e:
        print(f"   Failed to kill process on port {port}: {e}")
    return False


def check_dependencies() -> None:
    """Check if required commands are available."""
    print("\n🔍 Checking dependencies...\n")
    
    required = {
        "mvn": "Maven (for Backend)",
        "npm": "npm (for Frontend)",
        "python": "Python (for AI Service & Simulator)"
    }
    
    missing = []
    for cmd, description in required.items():
        if find_command(cmd):
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: NOT FOUND")
            missing.append(description)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Please install missing tools and ensure they're in your PATH")
        print("\nFor Windows, you may need to:")
        print("  - Install Maven and add to PATH")
        print("  - Install Node.js (includes npm) and add to PATH")
        print("  - Run setup-env.ps1 to configure environment variables")
        return False
    
    print("\n✅ All dependencies found\n")
    return True


def load_pids() -> Dict[str, int]:
    """Load stored PIDs from file."""
    if PIDS_FILE.exists():
        with open(PIDS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_pids(pids: Dict[str, int]) -> None:
    """Save PIDs to file."""
    with open(PIDS_FILE, 'w') as f:
        json.dump(pids, f, indent=2)


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        if sys.platform == "win32":
            # Windows
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Unix-like
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, OSError):
        return False


def start_service(service_key: str) -> bool:
    """Start a single service."""
    service = SERVICES[service_key]
    directory = service["directory"]
    start_cmd = service["start_cmd"]
    port = service["port"]
    
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return False
    
    # Check if port is in use and kill if needed
    if is_port_in_use(port):
        print(f"⚠️  Port {port} is in use, attempting to free it...")
        if not kill_process_on_port(port):
            print(f"❌ Could not free port {port}, skipping {service['name']}")
            return False
        time.sleep(1)
    
    # Check if the command is available
    cmd_name = start_cmd[0]
    cmd_path = find_command(cmd_name)
    if not cmd_path:
        print(f"❌ Command '{cmd_name}' not found in PATH")
        print(f"   Skipping {service['name']}")
        return False
    
    print(f"🚀 Starting {service['name']}...")
    
    try:
        # Use full path for the command on Windows
        cmd_with_path = [cmd_path] + start_cmd[1:]
        
        # For Python services, set PYTHONPATH to include the project root
        env = os.environ.copy()
        if cmd_name == "python":
            env["PYTHONPATH"] = str(directory)
        
        if sys.platform == "win32":
            # Windows: Use CREATE_NEW_PROCESS_GROUP to enable proper termination
            process = subprocess.Popen(
                cmd_with_path,
                cwd=directory,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                env=env
            )
        else:
            # Unix-like
            process = subprocess.Popen(
                cmd_with_path,
                cwd=directory,
                start_new_session=True,
                env=env
            )
        
        # Wait a moment to ensure process started successfully
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            print(f"❌ {service['name']} failed to start (exited immediately)")
            return False
        
        # Save PID
        pids = load_pids()
        pids[service_key] = process.pid
        save_pids(pids)
        
        print(f"✅ {service['name']} started (PID: {process.pid})")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start {service['name']}: {e}")
        return False


def stop_service(service_key: str) -> bool:
    """Stop a single service."""
    pids = load_pids()
    
    if service_key not in pids:
        print(f"⚠️  {SERVICES[service_key]['name']} not running (no PID found)")
        return False
    
    pid = pids[service_key]
    
    if not is_process_running(pid):
        print(f"⚠️  {SERVICES[service_key]['name']} not running (PID: {pid} not found)")
        del pids[service_key]
        save_pids(pids)
        return False
    
    print(f"🛑 Stopping {SERVICES[service_key]['name']} (PID: {pid})...")
    
    try:
        if sys.platform == "win32":
            # Windows: Send CTRL+BREAK to process group
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True
            )
        else:
            # Unix-like: Send SIGTERM to process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        
        # Wait a bit for graceful shutdown
        time.sleep(2)
        
        # Force kill if still running
        if is_process_running(pid):
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True
                )
            else:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
        
        del pids[service_key]
        save_pids(pids)
        print(f"✅ {SERVICES[service_key]['name']} stopped")
        return True
        
    except Exception as e:
        print(f"❌ Failed to stop {SERVICES[service_key]['name']}: {e}")
        return False


def start_all_services() -> None:
    """Start all services in order."""
    # Check dependencies first
    if not check_dependencies():
        print("\n⚠️  Skipping services with missing dependencies")
        print("You can still start services that have all dependencies available\n")
    
    print("\n🏁 Starting all services...\n")
    
    # Start in order: backend -> ai-service -> simulator -> frontend
    start_order = ["backend", "ai-service", "simulator", "frontend"]
    
    started = []
    for service_key in start_order:
        if start_service(service_key):
            started.append(service_key)
            # Wait a bit between services
            time.sleep(3)
    
    print("\n✨ Service startup complete!")
    print(f"\n📊 Services started: {len(started)}/{len(start_order)}")
    
    if started:
        print("\n📊 Access URLs:")
        if "frontend" in started:
            # Check if frontend is on expected port or auto-selected
            if is_port_in_use(3000):
                print(f"   Frontend:     http://localhost:3000")
            else:
                # Find the actual port Vite is using
                print(f"   Frontend:     Check Vite output for actual port (likely 5173-5176)")
        if "backend" in started:
            print(f"   Backend API:  http://localhost:8080")
            print(f"   H2 Console:   http://localhost:8080/h2-console")
        if "ai-service" in started:
            print(f"   AI Service:   http://localhost:8002")
        if "simulator" in started:
            print(f"   Simulator:    http://localhost:8001")
        print()


def stop_all_services() -> None:
    """Stop all services."""
    print("\n🛑 Stopping all services...\n")
    
    # Stop in reverse order: frontend -> simulator -> ai-service -> backend
    stop_order = ["frontend", "simulator", "ai-service", "backend"]
    
    for service_key in stop_order:
        stop_service(service_key)
    
    # Clean up PID file
    if PIDS_FILE.exists():
        PIDS_FILE.unlink()
    
    print("\n✨ All services stopped!\n")


def check_status() -> None:
    """Check status of all services."""
    print("\n📊 Service Status:\n")
    
    pids = load_pids()
    
    for service_key, service in SERVICES.items():
        if service_key in pids:
            pid = pids[service_key]
            if is_process_running(pid):
                print(f"✅ {service['name']}: RUNNING (PID: {pid})")
            else:
                print(f"❌ {service['name']}: STOPPED (PID: {pid} not found)")
                # Clean up stale PID
                del pids[service_key]
                save_pids(pids)
        else:
            print(f"❌ {service['name']}: STOPPED")
    
    print()


def restart_all_services() -> None:
    """Restart all services."""
    print("\n🔄 Restarting all services...\n")
    stop_all_services()
    time.sleep(2)
    start_all_services()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python manage-services.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all_services()
    elif command == "stop":
        stop_all_services()
    elif command == "status":
        check_status()
    elif command == "restart":
        restart_all_services()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python manage-services.py [start|stop|status|restart]")
        sys.exit(1)


if __name__ == "__main__":
    main()
