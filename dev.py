#!/usr/bin/env python3
"""
QWP Development Environment Setup Script (Direct TCP Mode)
Simplified and robust version to avoid tmux session creation issues.
"""

import platform
import subprocess
import sys
import time
from pathlib import Path
from shutil import which
from typing import Dict, List, Optional, Union

# Configure colors for console output
RESET = "\033[0m"
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"

# Configuration
PROJECT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
BACKEND_DIR = PROJECT_DIR / "backend"
SESSION_NAME = "hud_direct_tcp"
PYTHON_BACKEND_SCRIPT = "backend/main.py"
TCP_PORT = 35000
UV_ENABLED = True

# Will be set during runtime
VENV_PATH = PROJECT_DIR / ".venv"
VENV_ACTIVATE_SCRIPT = VENV_PATH / "bin" / "activate"
PYTHON_INTERPRETER = VENV_PATH / "bin" / "python"
ELM_CMD = VENV_PATH / "bin" / "elm"
PYTHON_EXEC_CMD = []


def log(message: str) -> None:
    """Print info message."""
    print(f"{CYAN}[INFO]{RESET} {message}")

def warn(message: str) -> None:
    """Print warning message."""
    print(f"{YELLOW}[WARN]{RESET} {message}", file=sys.stderr)

def error(message: str) -> None:
    """Print error message and exit."""
    print(f"{RED}[ERROR]{RESET} {message}", file=sys.stderr)
    sys.exit(1)

def success(message: str) -> None:
    """Print success message."""
    print(f"{GREEN}[SUCCESS]{RESET} {message}")

def print_separator() -> None:
    """Print a separator line."""
    print("-" * 68)

def get_os() -> str:
    """Return the current operating system."""
    system = platform.system()
    if system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "macOS"
    return f"UNKNOWN:{system}"

def run_cmd(cmd: Union[str, List[str]], shell: bool = False, 
           capture_output: bool = False, check: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command and handle errors."""
    try:
        if shell and isinstance(cmd, list):
            cmd = " ".join(cmd)
        return subprocess.run(cmd, shell=shell, text=True, 
                             capture_output=capture_output, check=check)
    except subprocess.SubprocessError as e:
        if check:
            error(f"Command failed: {e}")
        return subprocess.CompletedProcess(cmd, 1, "", str(e))

def cmd_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return which(cmd) is not None

def ask_yes_no(question: str) -> bool:
    """Ask a yes/no question."""
    response = input(f"{question} (y/n) ").lower().strip()
    return response in ('y', 'yes')

def install_system_dependency(cmd_name: str, install_cmd_macos: str, install_cmd_linux: str) -> None:
    """Check and install system dependencies if needed."""
    if cmd_exists(cmd_name):
        return
        
    warn(f"'{cmd_name}' not found.")
    if not ask_yes_no(f"Install '{cmd_name}'?"):
        error(f"'{cmd_name}' is required.")

    os_type = get_os()
    log(f"Installing '{cmd_name}'...")
    
    if os_type == "macOS":
        result = run_cmd(install_cmd_macos, shell=True)
        if result.returncode != 0:
            error(f"Failed to install '{cmd_name}' (macOS).")
    elif os_type == "Linux":
        result = run_cmd(f"sudo {install_cmd_linux}", shell=True)
        if result.returncode != 0:
            error(f"Failed to install '{cmd_name}' (Linux).")
    else:
        warn(f"Unsupported OS for auto-install of '{cmd_name}'.")
        return

    if not cmd_exists(cmd_name):
        error(f"'{cmd_name}' still not found after install.")
    
    success(f"'{cmd_name}' installed.")

def install_uv() -> None:
    """Check and install uv if needed."""
    if cmd_exists("uv"):
        return
        
    warn("'uv' not found.")
    if not ask_yes_no("Install 'uv'?"):
        error("'uv' is required if UV_ENABLED=true.")

    log("Installing 'uv'...")
    result = run_cmd("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True)
    if result.returncode != 0:
        error("Failed to install 'uv'.")
        
    warn("UV installed. May need new terminal or PATH update (e.g. source ~/.cargo/env).")
    
    if not cmd_exists("uv"):
        error("'uv' still not found. Check your PATH and restart the script.")
        
    success("'uv' installed.")

def setup_python_environment() -> None:
    """Set up Python virtual environment."""
    global VENV_PATH, VENV_ACTIVATE_SCRIPT, PYTHON_INTERPRETER, ELM_CMD, PIP_CMD, PIP_LIST_CMD
    
    log(f"Setting up Python environment in {PROJECT_DIR}...")
    
    if UV_ENABLED:
        install_uv()
        log(f"Ensuring uv virtual environment exists at {VENV_PATH}...")
        
        result = run_cmd(["uv", "venv"], shell=True)
        if result.returncode != 0:
            error(f"Failed to setup/ensure uv environment at {VENV_PATH}. 'uv venv' command failed.")
            
        PIP_CMD = ["uv", "pip"]
        PIP_LIST_CMD = ["uv", "pip", "list"]
    else:
        venv_dirs = [".venv", "venv", "env"]
        found_venv = False
        
        for venv_dir_name in venv_dirs:
            potential_venv_path = PROJECT_DIR / venv_dir_name
            if (potential_venv_path / "bin" / "activate").exists():
                VENV_PATH = potential_venv_path
                VENV_ACTIVATE_SCRIPT = VENV_PATH / "bin" / "activate"
                log(f"Found traditional venv at {VENV_PATH}")
                found_venv = True
                break
                
        if not found_venv:
            warn("No traditional venv found & UV_ENABLED=false.")
            if not ask_yes_no("Continue?"):
                sys.exit(1)
            VENV_ACTIVATE_SCRIPT = None
            
        PIP_CMD = ["pip"]
        PIP_LIST_CMD = ["pip", "list"]
        
    PYTHON_INTERPRETER = VENV_PATH / "bin" / "python"
    ELM_CMD = VENV_PATH / "bin" / "elm"

def check_python_dependencies() -> None:
    """Check if required Python packages are installed."""
    python_packages = ["ELM327-emulator", "websockets", "pyserial", "obd"]
    
    log(f"Checking Python package dependencies using '{' '.join(PIP_CMD)}'...")
    
    if not cmd_exists(PIP_CMD[0]):
        warn(f"Cannot check Python pkgs. '{PIP_CMD[0]}' not found.")
        if not ask_yes_no("Continue?"):
            sys.exit(1)
        return
        
    # Get installed packages
    result = run_cmd(PIP_LIST_CMD, capture_output=True)
    if result.returncode != 0:
        warn(f"Cannot check Python pkgs. '{' '.join(PIP_LIST_CMD)}' failed.")
        if not ask_yes_no("Continue?"):
            sys.exit(1)
        return

    # Parse installed packages
    installed_packages = {
        line.lower().split()[0] for line in result.stdout.splitlines()[2:]
        if line.strip()
    }

    # Check which packages are missing
    missing_packages = [
        pkg for pkg in python_packages
        if pkg.lower() not in installed_packages
    ]
    
    if missing_packages:
        warn("Missing Python packages:")
        for pkg in missing_packages:
            warn(f"  - {pkg}")
            
        if ask_yes_no(f"Install missing Python packages using '{' '.join(PIP_CMD)}'?"):
            log(f"Installing: {' '.join(missing_packages)}...")
            install_cmd = [*PIP_CMD, "install", *missing_packages]
            result = run_cmd(install_cmd)
            if result.returncode != 0:
                error("Failed to install Python packages.")
            success("Python packages installed.")
        else:
            error("Required Python packages missing.")
    else:
        log("Python packages seem installed.")
        
    # Check for elm
    if not (ELM_CMD.exists() or cmd_exists("elm")):
        warn(f"'elm' not found via '{ELM_CMD}' or PATH. Tmux panes might fail if ELM327-emulator not installed in venv.")

def check_watchexec() -> None:
    """Check for watchexec and configure hot reloading."""
    global PYTHON_EXEC_CMD
    
    log("Checking for watchexec...")
    python_run_cmd = [str(PYTHON_INTERPRETER), PYTHON_BACKEND_SCRIPT]
    PYTHON_EXEC_CMD = python_run_cmd.copy()
    
    if cmd_exists("watchexec"):
        log("watchexec found - hot-reload enabled.")
        PYTHON_EXEC_CMD = [
            "watchexec", "--shell=none", "-w", "./backend", 
            "-e", "py", "--clear", "--restart", "--", 
            *python_run_cmd
        ]
    else:
        warn("watchexec not found. Hot-reload disabled.")
        if ask_yes_no("Install 'watchexec'?"):
            os_type = get_os()
            
            if os_type == "macOS" and cmd_exists("brew"):
                log("Installing 'watchexec' (Homebrew)...")
                result = run_cmd("brew install watchexec", shell=True)
                if result.returncode != 0:
                    warn("Homebrew install failed.")
            elif PIP_CMD and cmd_exists(PIP_CMD[0]):
                log(f"Installing 'watchexec-cli'...")
                install_cmd = [*PIP_CMD, "install", "watchexec-cli"]
                result = run_cmd(install_cmd)
                if result.returncode != 0:
                    warn("pip install failed.")
            else:
                warn("Cannot auto-install 'watchexec'. Install manually.")
                
            if cmd_exists("watchexec"):
                success("'watchexec' installed.")
                PYTHON_EXEC_CMD = [
                    "watchexec", "--shell=none", "-w", "./backend", 
                    "-e", "py", "--clear", "--restart", "--", 
                    *python_run_cmd
                ]
            else:
                warn("'watchexec' still not found.")
        else:
            log("Proceeding without 'watchexec'.")

def check_project_files() -> None:
    """Check if required project files exist."""
    log("Checking project file structure...")
    
    if not PROJECT_DIR.is_dir():
        error(f"Project dir not found: {PROJECT_DIR}")
        
    if not FRONTEND_DIR.is_dir():
        error(f"Frontend dir not found: {FRONTEND_DIR}")
        
    if not BACKEND_DIR.is_dir():
        error(f"Backend dir not found: {BACKEND_DIR}")
        
    if not (PROJECT_DIR / PYTHON_BACKEND_SCRIPT).is_file():
        error(f"Backend script not found: {PROJECT_DIR / PYTHON_BACKEND_SCRIPT}")
        
    if not (FRONTEND_DIR / "package.json").is_file():
        error(f"No package.json in frontend: {FRONTEND_DIR}")

def create_tmux_script() -> Path:
    """Create a bash script that sets up the tmux session.
    
    This approach is much more reliable than trying to set up the tmux
    session directly from Python, especially in environments where
    window/pane manipulations are problematic.
    """
    tmux_script_path = PROJECT_DIR / "tmux_setup_temp.sh"
    
    # Convert paths to strings for the script
    project_dir_str = str(PROJECT_DIR)
    frontend_dir_str = str(FRONTEND_DIR)
    venv_activate_str = str(VENV_ACTIVATE_SCRIPT)
    elm_cmd_str = str(ELM_CMD)
    python_exec_cmd_str = " ".join(str(x) for x in PYTHON_EXEC_CMD)
    
    script_content = f"""#!/bin/bash
# Temporary tmux setup script generated by dev.py

# Kill existing session if it exists
tmux kill-session -t {SESSION_NAME} 2>/dev/null || true

# Create new detached session with a terminal type that doesn't require size
TERM=dumb tmux new-session -d -s {SESSION_NAME}

# Rename the window
tmux rename-window -t {SESSION_NAME}:0 "HUD_Direct"

# Set up the working directory for pane 0
tmux send-keys -t {SESSION_NAME}:0.0 "cd {project_dir_str}" C-m
sleep 0.5

# Set appearance
tmux set-option -g -t {SESSION_NAME} status-right "QWP Direct TCP | %H:%M %d-%b-%y"
tmux set-option -g -t {SESSION_NAME} status-style "bg=blue,fg=white"

# Pane 0: Car Emulator
tmux send-keys -t {SESSION_NAME}:0.0 "source {venv_activate_str}" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.0 "echo '>>> PANE 0: Starting Car Emulator (TCP) on port {TCP_PORT}...'" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.0 "echo 'You can type: loglevel debug'" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.0 "\\\"{elm_cmd_str}\\\" -s car -n {TCP_PORT} || {{ echo 'PANE 0 ERROR: Car emulator failed to start!'; }}" C-m
sleep 0.5

# Create pane 1 for Python Backend
tmux split-window -h -t {SESSION_NAME}:0.0
sleep 0.5

# Pane 1: Python Backend
tmux send-keys -t {SESSION_NAME}:0.1 "cd {project_dir_str}" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.1 "source {venv_activate_str}" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.1 "echo '>>> PANE 1: Starting Python Backend (Direct TCP to port {TCP_PORT})...'" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.1 "echo 'Ensure backend/main.py is configured for direct TCP'" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.1 "{python_exec_cmd_str} || {{ echo 'PANE 1 ERROR: Python backend failed to start!'; }}" C-m
sleep 0.5

# Create pane 2 for Frontend
tmux split-window -v -t {SESSION_NAME}:0.1
sleep 0.5

# Pane 2: Frontend
tmux send-keys -t {SESSION_NAME}:0.2 "cd {frontend_dir_str}" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.2 "echo '>>> PANE 2: Starting Vue Frontend Dev Server...'" C-m
sleep 0.3
tmux send-keys -t {SESSION_NAME}:0.2 "npm run dev || {{ echo 'PANE 2 ERROR: Frontend dev server failed to start!'; }}" C-m

# Select pane 1 as active
tmux select-pane -t {SESSION_NAME}:0.1
"""

    # Write script to file
    with open(tmux_script_path, "w") as f:
        f.write(script_content)
    
    # Make it executable
    tmux_script_path.chmod(0o755)
    
    return tmux_script_path

def setup_tmux_session() -> None:
    """Set up tmux session using a bash script helper."""
    log(f"Setting up tmux session '{SESSION_NAME}' (Direct TCP - 3 Panes)...")
    
    # Create a temporary script to set up the tmux session
    tmux_script = create_tmux_script()
    
    try:
        # Run the script
        result = run_cmd([str(tmux_script)], check=True)
        if result.returncode != 0:
            error("Failed to set up tmux session.")
    finally:
        # Clean up the temporary script
        try:
            tmux_script.unlink()
        except Exception as e:
            warn(f"Failed to delete temporary script: {e}")

def show_instructions() -> None:
    """Display usage instructions."""
    print_separator()
    log(f"Tmux session {SESSION_NAME} (Direct TCP) with window HUD_Direct is ready.")
    log("Instructions for use:")
    print(f"1. Pane 0 (Left) runs the Car Emulator on TCP port {TCP_PORT}.")
    print("   (You can type 'loglevel debug' at its CMD> prompt for more details).")
    print("2. Pane 1 (Right-Top) runs the Python Backend.")
    print(f"   It should connect to the Car Emulator directly via 'socket://localhost:{TCP_PORT}'.")
    print("   If watchexec is running, changes to backend/main.py will restart it.")
    print("3. Pane 2 (Right-Bottom) runs the Vue.js dev server.")
    print_separator()
    log("Tmux Keyboard Shortcuts:")
    print("- Prefix: Ctrl+B")
    print("- Navigate panes: Prefix, Arrow Keys")
    print("- Detach: Prefix, d")
    print(f"- Reattach: tmux attach -t {SESSION_NAME}")
    print_separator()

def main() -> None:
    """Main entry point."""
    print_separator()
    log("QWP Development Environment Setup Script (Direct TCP Mode)")
    print_separator()
    
    # Check system dependencies
    install_system_dependency("tmux", "brew install tmux", "apt-get install -y tmux")
    install_system_dependency("node", "brew install node", "apt-get install -y nodejs")
    install_system_dependency("npm", "brew install npm", "apt-get install -y npm")
    
    # Setup environment
    check_project_files()
    setup_python_environment()
    check_python_dependencies()
    check_watchexec()
    
    # Setup tmux session
    setup_tmux_session()
    show_instructions()
    
    success(f"Attaching to tmux session {SESSION_NAME}...")
    
    # Attach to the tmux session
    attach_result = run_cmd(["tmux", "attach-session", "-t", SESSION_NAME])
    
    log(f"Detached from tmux session '{SESSION_NAME}'.")

if __name__ == "__main__":
    main()
