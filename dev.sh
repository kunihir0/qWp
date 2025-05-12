#!/bin/bash
set -e  # Exit on error

# ==== CONFIGURATION - Edit these variables to match your setup ====
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
SESSION_NAME="hud_direct_tcp" # Session name for direct TCP
# These will be updated by setup_python_environment to point to venv specifics
PYTHON_INTERPRETER_CMD="python" 
ELM_CMD="elm" 
PYTHON_BACKEND_SCRIPT="backend/main.py"
TCP_PORT=35000   # Port for car emulator

# Support for uv package manager
UV_ENABLED=true  # Set to false to use traditional venv activation instead

# ==== UTILITY FUNCTIONS ====
log() { echo -e "\033[1;36m[INFO]\033[0m $1"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $1" >&2; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $1" >&2; exit 1; }
success() { echo -e "\033[1;32m[SUCCESS]\033[0m $1"; }
print_separator() { echo "--------------------------------------------------------------------"; }

get_os() {
  OS_NAME=""
  case "$(uname -s)" in
    Linux*)     OS_NAME="Linux";;
    Darwin*)    OS_NAME="macOS";;
    *)          OS_NAME="UNKNOWN:$(uname -s)"
  esac
  echo "$OS_NAME"
}

# ==== DEPENDENCY INSTALLATION FUNCTIONS ====
install_system_dependency() {
  local cmd_name="$1"; local install_cmd_macos="$2"; local install_cmd_linux="$3"; local os_type=$(get_os)
  if ! command -v "$cmd_name" &> /dev/null; then
    warn "'$cmd_name' not found." && read -p "Install '$cmd_name'? (y/n) " -n 1 -r && echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      log "Installing '$cmd_name'..."
      if [ "$os_type" == "macOS" ]; then eval "$install_cmd_macos" || error "Failed to install '$cmd_name' (macOS).";
      elif [ "$os_type" == "Linux" ]; then eval "sudo $install_cmd_linux" || error "Failed to install '$cmd_name' (Linux).";
      else warn "Unsupported OS for auto-install of '$cmd_name'."; return 1; fi
      command -v "$cmd_name" &> /dev/null || error "'$cmd_name' still not found after install."
      success "'$cmd_name' installed."
    else error "'$cmd_name' is required."; fi
  fi
}
install_uv() {
  if ! command -v uv &> /dev/null; then
    warn "'uv' not found." && read -p "Install 'uv'? (y/n) " -n 1 -r && echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      log "Installing 'uv'..." && curl -LsSf https://astral.sh/uv/install.sh | sh || error "Failed to install 'uv'."
      warn "UV installed. May need new terminal or PATH update (e.g. source \$HOME/.cargo/env)."
      command -v uv &> /dev/null || error "'uv' still not found. Check PATH."
      success "'uv' installed."
    else error "'uv' is required if UV_ENABLED=true."; fi
  fi
}

# ==== DEPENDENCY CHECKS ====
setup_python_environment() {
  log "Setting up Python environment in ${PROJECT_DIR}..."
  VENV_PATH="${PROJECT_DIR}/.venv"
  VENV_ACTIVATE_SCRIPT="${VENV_PATH}/bin/activate"
  
  if [ "$UV_ENABLED" = true ]; then
    install_uv 
    log "Ensuring uv virtual environment exists at ${VENV_PATH}..."
    (cd "${PROJECT_DIR}" && uv venv > /dev/null 2>&1) || error "Failed to setup/ensure uv environment at ${VENV_PATH}. 'uv venv' command failed." 
    PIP_CMD="uv pip" 
    PIP_LIST_CMD="uv pip list" 
  else
    VENV_DIRS=(".venv" "venv" "env"); local found_venv=false
    for venv_dir_name in "${VENV_DIRS[@]}"; do potential_venv_path="${PROJECT_DIR}/${venv_dir_name}"; if [ -f "${potential_venv_path}/bin/activate" ]; then VENV_PATH="${potential_venv_path}"; VENV_ACTIVATE_SCRIPT="${VENV_PATH}/bin/activate"; log "Found traditional venv at ${VENV_PATH}"; found_venv=true; break; fi; done
    if [ "$found_venv" = false ]; then warn "No traditional venv found & UV_ENABLED=false." && read -p "Continue? (y/n) " -n 1 -r && echo && [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1; VENV_ACTIVATE_SCRIPT=""; fi
    PIP_CMD="pip"; PIP_LIST_CMD="pip list"
  fi
  PYTHON_INTERPRETER_CMD="${VENV_PATH}/bin/python"; ELM_CMD="${VENV_PATH}/bin/elm"
  if [ -n "$VENV_ACTIVATE_SCRIPT" ] && [ -f "$VENV_ACTIVATE_SCRIPT" ]; then log "Activating env for script: source ${VENV_ACTIVATE_SCRIPT}"; source "${VENV_ACTIVATE_SCRIPT}"; else warn "No venv activated for script checks."; fi
}
check_python_dependencies() {
  log "Checking Python package dependencies using '${PIP_CMD}'..."
  PYTHON_PACKAGE_DEFINITIONS=("ELM327-emulator:ELM327-emulator" "websockets:websockets" "pyserial:pyserial" "obd:obd")
  MISSING_PY_PACKAGES_TO_INSTALL=()
  local base_pip_cmd="${PIP_CMD%% *}"; if ! command -v "$base_pip_cmd" &> /dev/null || ! $PIP_LIST_CMD &> /dev/null ; then warn "Cannot check Python pkgs. '${PIP_LIST_CMD}' failed or '${base_pip_cmd}' not found." && read -p "Continue? (y/n) " -n 1 -r && echo && [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1; return; fi
  for definition in "${PYTHON_PACKAGE_DEFINITIONS[@]}"; do check_name_in_list="${definition%%:*}"; install_target="${definition#*:}"; if ! $PIP_LIST_CMD | grep -i "^${check_name_in_list}\b" &> /dev/null; then MISSING_PY_PACKAGES_TO_INSTALL+=("$install_target"); fi; done
  if [ ${#MISSING_PY_PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
    warn "Missing Python packages:"; INSTALL_PY_CMDS_STR="" 
    for pkg_to_install in "${MISSING_PY_PACKAGES_TO_INSTALL[@]}"; do warn "  - ${pkg_to_install}"; INSTALL_PY_CMDS_STR+="${pkg_to_install} "; done
    read -p "Install missing Python packages using '${PIP_CMD}'? (y/n) " -n 1 -r && echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then log "Installing: ${INSTALL_PY_CMDS_STR}..."; eval "$PIP_CMD install $INSTALL_PY_CMDS_STR" || error "Failed to install Python packages."; success "Python packages installed."; else error "Required Python packages missing."; fi
  else log "Python packages seem installed."; fi
  if ! [ -x "$ELM_CMD" ] && ! command -v elm &> /dev/null ; then warn "'elm' not found via '${ELM_CMD}' or PATH. Tmux panes might fail if ELM327-emulator not installed in venv."; fi
}
check_watchexec() {
  log "Checking for watchexec..."; PYTHON_RUN_CMD="\"${PYTHON_INTERPRETER_CMD}\" ${PYTHON_BACKEND_SCRIPT}"; PYTHON_EXEC_CMD="${PYTHON_RUN_CMD}" 
  if command -v watchexec &> /dev/null; then log "watchexec found - hot-reload enabled."; PYTHON_EXEC_CMD="watchexec --shell=none -w ./backend -e py --clear --restart -- ${PYTHON_RUN_CMD}";
  else
    warn "watchexec not found. Hot-reload disabled."; read -p "Install 'watchexec'? (y/n) " -n 1 -r && echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      local os_type=$(get_os); local pip_base_cmd_for_watchexec="${PIP_CMD%% *}"
      if [ "$os_type" == "macOS" ] && command -v brew &> /dev/null; then log "Installing 'watchexec' (Homebrew)..."; brew install watchexec || warn "Homebrew install failed.";
      elif [ -n "$PIP_CMD" ] && command -v "$pip_base_cmd_for_watchexec" &> /dev/null; then log "Installing 'watchexec-cli' (${PIP_CMD})..."; ${PIP_CMD} install watchexec-cli || warn "${PIP_CMD} install failed.";
      else warn "Cannot auto-install 'watchexec'. Install manually."; fi
      if command -v watchexec &> /dev/null; then success "'watchexec' installed."; PYTHON_EXEC_CMD="watchexec --shell=none -w ./backend -e py --clear --restart -- ${PYTHON_RUN_CMD}"; else warn "'watchexec' still not found."; fi
    else log "Proceeding without 'watchexec'."; fi
  fi
}
check_project_files() {
  log "Checking project file structure..."; if [ ! -d "$PROJECT_DIR" ]; then error "Project dir not found: $PROJECT_DIR"; fi; if [ ! -d "$FRONTEND_DIR" ]; then error "Frontend dir not found: $FRONTEND_DIR"; fi; if [ ! -d "${PROJECT_DIR}/backend" ]; then error "Backend dir not found: ${PROJECT_DIR}/backend"; fi; if [ ! -f "${PROJECT_DIR}/${PYTHON_BACKEND_SCRIPT}" ]; then error "Backend script not found: ${PROJECT_DIR}/${PYTHON_BACKEND_SCRIPT}"; fi; if [ ! -f "${FRONTEND_DIR}/package.json" ]; then error "No package.json in frontend: ${FRONTEND_DIR}"; fi
}

# ==== TMUX SESSION SETUP (Simplified for Direct TCP - 3 Panes) ====
setup_tmux_session() {
  log "Setting up tmux session '${SESSION_NAME}' (Direct TCP - 3 Panes)..."
  tmux kill-session -t $SESSION_NAME 2>/dev/null || true
  
  # Create new detached session, name the first window, and get the ID of the first pane (Pane 0)
  tmux new-session -d -s $SESSION_NAME -c "${PROJECT_DIR}" -n "HUD_Direct" -P -F "#{pane_id}"
  local PANE0_ID=$(tmux display-message -p -t $SESSION_NAME:HUD_Direct.0 '#{pane_id}')
  
  tmux set-option -g -t $SESSION_NAME status-right "QWP Direct TCP | %H:%M %d-%b-%y" 
  tmux set-option -g -t $SESSION_NAME status-style "bg=blue,fg=white" # Different color for this setup

  local tmux_venv_activate_cmd="source \"${VENV_PATH}/bin/activate\""
  if [ ! -f "${VENV_PATH}/bin/activate" ]; then
      warn "Venv activate script not found at ${VENV_PATH}/bin/activate for tmux. Panes might fail."
      tmux_venv_activate_cmd="echo 'Warning: venv activate script for pane not found at ${VENV_PATH}/bin/activate.'"
  fi
  
  # Pane 0 (Left - 50% width): Car Emulator (TCP)
  tmux send-keys -t "${PANE0_ID}" "${tmux_venv_activate_cmd}" C-m; sleep 0.3
  tmux send-keys -t "${PANE0_ID}" "echo '>>> PANE 0 (Left): Starting Car Emulator (TCP) on port ${TCP_PORT}...'" C-m; sleep 0.3
  tmux send-keys -t "${PANE0_ID}" "echo 'You can type: loglevel debug'" C-m; sleep 0.3
  tmux send-keys -t "${PANE0_ID}" "\"${ELM_CMD}\" -s car -n ${TCP_PORT} || { echo 'PANE 0 ERROR: Car emulator failed to start!'; }" C-m

  # Split Pane 0 horizontally to create Pane 1 (Right side, will be split further)
  tmux split-window -h -p 66 -t "${PANE0_ID}" -c "${PROJECT_DIR}" -P -F "#{pane_id}" 
  local PANE1_ID=$(tmux display-message -p -t $SESSION_NAME:HUD_Direct.#{window_last_pane} '#{pane_id}') 
  sleep 0.3
  
  # Pane 1 (Right-Top): Python Backend
  tmux send-keys -t "${PANE1_ID}" "${tmux_venv_activate_cmd}" C-m; sleep 0.3
  tmux send-keys -t "${PANE1_ID}" "echo '>>> PANE 1 (Right-Top): Starting Python Backend (Direct TCP to port ${TCP_PORT})...'" C-m; sleep 0.3
  tmux send-keys -t "${PANE1_ID}" "echo 'Ensure backend/main.py is configured for direct TCP (socket://localhost:${TCP_PORT})'" C-m; sleep 0.3
  tmux send-keys -t "${PANE1_ID}" "${PYTHON_EXEC_CMD} || { echo 'PANE 1 ERROR: Python backend failed to start!'; }" C-m
  
  # Split Pane 1 vertically to create Pane 2 (Right-Bottom): Frontend
  tmux select-pane -t "${PANE1_ID}"; sleep 0.3 
  tmux split-window -v -p 50 -t "${PANE1_ID}" -c "${FRONTEND_DIR}" -P -F "#{pane_id}"
  local PANE2_ID=$(tmux display-message -p -t $SESSION_NAME:HUD_Direct.#{window_last_pane} '#{pane_id}')
  sleep 0.3
  tmux send-keys -t "${PANE2_ID}" "echo '>>> PANE 2 (Right-Bottom): Starting Vue Frontend Dev Server...'" C-m; sleep 0.3
  tmux send-keys -t "${PANE2_ID}" "npm run dev || { echo 'PANE 2 ERROR: Frontend dev server failed to start!'; }" C-m

  tmux select-pane -t "${PANE1_ID}" # Default active pane (Python Backend)
}

# ==== MAIN EXECUTION ====
main() {
  print_separator
  log "QWP Development Environment Setup Script (Direct TCP Mode)"
  print_separator
  
  install_system_dependency "tmux" "brew install tmux" "apt-get install -y tmux"
  install_system_dependency "node" "brew install node" "apt-get install -y nodejs" 
  install_system_dependency "npm" "brew install npm" "apt-get install -y npm" 

  check_project_files
  setup_python_environment 
  check_python_dependencies 
  check_watchexec 

  setup_tmux_session 
  
  print_separator
  log "Tmux session ${SESSION_NAME} (Direct TCP) with window HUD_Direct is ready."
  log "Instructions for use:"
  echo "1. Pane 0 (Left) runs the Car Emulator on TCP port ${TCP_PORT}."
  echo "   (You can type 'loglevel debug' at its CMD> prompt for more details)."
  echo "2. Pane 1 (Right-Top) runs the Python Backend."
  echo "   It should connect to the Car Emulator directly via 'socket://localhost:${TCP_PORT}'."
  echo "   Ensure your backend/main.py is the version configured for direct TCP."
  echo "   If watchexec is running, changes to backend/main.py will restart it."
  echo "3. Pane 2 (Right-Bottom) runs the Vue.js dev server."
  print_separator
  log "Tmux Keyboard Shortcuts:"
  echo "- Prefix: Ctrl+B"
  echo "- Navigate panes: Prefix, Arrow Keys"
  echo "- Detach: Prefix, d"
  echo "- Reattach: tmux attach -t ${SESSION_NAME}"
  print_separator
  
  success "Attaching to tmux session ${SESSION_NAME}..."
  
  tmux attach-session -t $SESSION_NAME
  
  log "Detached from tmux session '${SESSION_NAME}'."
}

# Run the main function
main "$@"
