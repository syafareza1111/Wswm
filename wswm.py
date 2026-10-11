import os
import json
import subprocess
import sys
import time

# --- AUTO-BOOTSTRAP DEPENDENCIES & ESSENTIAL UTILITIES ---
def ensure_dependencies():
    venv_dir = os.path.expanduser("~/wswm/venv")
    pip_path = os.path.join(venv_dir, "bin", "pip")
    python_path = os.path.join(venv_dir, "bin", "python")

    system_packages = [
        "python", "python-pip", "python-virtualenv",
        "xorg-server", "xorg-xinit", "xorg-xinput", "xorg-xrandr", "xorg-xdpyinfo",
        "xf86-input-libinput", "libinput", "touchegg", "xdotool", "libnotify", "networkmanager",
        "bluez", "bluez-utils", "pipewire", "pipewire-pulse", "wireplumber",
        "brightnessctl", "tlp", "curl", "git", "base-devel", "konsole"
    ]
    try:
        subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + system_packages, check=True)
    except Exception as e:
        print(f"[!] System package installation warning: {e}")

    if not os.path.exists(venv_dir) or sys.executable != python_path:
        print("[WSWM-Bootstrap] Initializing isolated virtual environment architecture...")
        if not os.path.exists(venv_dir):
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "google-genai", "python-xlib"], check=True)
        os.execve(python_path, [python_path] + sys.argv, os.environ)

ensure_dependencies()

from google import genai
from google.genai import types

CONFIG_PATH = os.path.expanduser("~/wswm/logs/config.json")
AUDIT_PATH = os.path.expanduser("~/wswm/logs/live_hardware_audit.json")

def load_or_init_config():
    default_config = {
        "GEMINI_API_KEY": "",
        "default_terminal": "konsole",
        "display_server": "x11",
        "display_manager": "sddm",
        "hardware_optimized": False,
        "network_configured": False,
        "browser_installed": False,
        "session_registered": False
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                default_config.update(json.load(f))
        except Exception as e:
            print(f"[!] Config load error, falling back to defaults: {e}")
    else:
        save_config(default_config)
    return default_config

def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"[!] Critical config save error: {e}")

def get_or_set_api_key(config):
    if config.get("GEMINI_API_KEY"):
        return config["GEMINI_API_KEY"]
    print("\n" + "="*60)
    print("        ARCH AI NEURAL SUITE - AUTHENTICATION REQUIRED")
    print("="*60)
    api_key = input("Enter your personal Gemini API Key: ").strip()
    if api_key:
        config["GEMINI_API_KEY"] = api_key
        save_config(config)
        print("[+] API Key successfully secured and stored in local configuration.\n")
        return api_key
    else:
        print("[!] Fatal: API Key required for neural engine initialization.")
        sys.exit(1)

def perform_audit():
    audit_data = {}
    try:
        audit_data["cpu"] = subprocess.run("lscpu | grep 'Model name' | cut -d: -f2", shell=True, capture_output=True, text=True).stdout.strip()
        audit_data["memory"] = subprocess.run("free -h | grep Mem | awk '{print $2}'", shell=True, capture_output=True, text=True).stdout.strip()
        audit_data["gpu"] = subprocess.run("lspci | grep -i vga | cut -d: -f3", shell=True, capture_output=True, text=True).stdout.strip()
        audit_data["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S')
        os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
        with open(AUDIT_PATH, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=4)
    except Exception as e:
        audit_data["error"] = str(e)
    return audit_data

def execute_action(command):
    cleaned = command.replace("```bash", "").replace("```", "").strip()
    try:
        print(f"\n[Neural Execution - {time.strftime('%H:%M:%S')}]:\n{cleaned}\n" + "-"*40)
        result = subprocess.run(cleaned, shell=True, text=True, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"[!] Execution exception encountered: {e}")
        return False

def call_gemini(client, prompt):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=1024)
        )
        return response.text if response and response.text else ""
    except Exception as e:
        print(f"[!] Neural Gateway Error: {e}")
        return ""

def setup_wizard(client, hw_profile, config):
    if not config.get("network_configured"):
        print("\n--- ARCH AI SETUP: NETWORK CONFIGURATION ---")
        subprocess.run("sudo systemctl enable --now NetworkManager", shell=True, capture_output=True)
        if input("Scan and configure wireless network interfaces now? (y/n): ").strip().lower() == 'y':
            subprocess.run("nmcli device wifi rescan && nmcli device wifi list", shell=True)
            ssid = input("Target Wireless SSID: ").strip()
            if ssid:
                pwd = input(f"Passphrase for {ssid} (leave empty for open networks): ").strip()
                cmd = f"nmcli device wifi connect '{ssid}' password '{pwd}'" if pwd else f"nmcli device wifi connect '{ssid}'"
                execute_action(cmd)
        config["network_configured"] = True
        save_config(config)

    if not config.get("hardware_optimized"):
        print("\n--- ARCH AI SETUP: HARDWARE KERNEL OPTIMIZATION ---")
        prompt = (
            "System Engineer Arch Linux. Hardware context: " + json.dumps(hw_profile) +
            " Provide optimized shell commands to install and configure: "
            "1. Advanced libinput touchpad multi-finger drivers and touchegg daemon. "
            "2. Curated cursor themes (capitaine-cursors) and unclutter utility. "
            "3. Bluetooth submodules (bluez) and PipeWire audio subsystem. "
            "4. Power management daemons (tlp, brightnessctl). "
            "Output strictly executable bash code blocks without commentary."
        )
        cmd = call_gemini(client, prompt)
        if cmd and input("Authorize and execute hardware driver payload? (y/n): ").strip().lower() == 'y':
            if execute_action(cmd):
                config["hardware_optimized"] = True
                save_config(config)

    if not config.get("browser_installed"):
        print("\n--- ARCH AI SETUP: NEURAL BROWSER DEPLOYMENT ---")
        if input("Deploy Brave Browser via AUR/Yay repository? (y/n): ").strip().lower() == 'y':
            install_cmd = (
                "sudo pacman -S --needed --noconfirm curl git base-devel && "
                "(which yay || (git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin && cd /tmp/yay-bin && makepkg -si --noconfirm)) && "
                "yay -S --needed --noconfirm brave-bin"
            )
            if execute_action(install_cmd):
                config["browser_installed"] = True
                save_config(config)

    print("\n--- ARCH AI SETUP: DISPLAY PROTOCOL & MANAGER ---")
    print("[1] X11 Protocol (Production Stable - Recommended)")
    print("[2] Wayland Protocol (Next-Gen Compositor)")
    choice = input("Select display backend [1/2] (Default 1): ").strip()
    backend = "wayland" if choice == "2" else "x11"
    config["display_server"] = backend

    # --- AUTO-BOOTSTRAP UTILITIES FOR CHOSEN BACKEND ---
    if backend == "wayland":
        print("\n[+] Auto-installing Wayland protocol & compositor packages...")
        subprocess.run("sudo pacman -S --needed --noconfirm wayland weston xorg-xwayland", shell=True)
    else:
        print("\n[+] Auto-installing X11 display server packages...")
        subprocess.run("sudo pacman -S --needed --noconfirm xorg-server xorg-xinit xdotool xdpyinfo xrandr", shell=True)

    print("\n[1] SDDM Display Manager (KDE Ecosystem)")
    print("[2] GDM Display Manager (GNOME Ecosystem)")
    print("[3] LightDM Display Manager (Lightweight)")
    print("[4] Manual Session Initialization (Skip DM)")
    dm_choice = input("Select Display Manager daemon [1-4] (Default 1): ").strip()
    dm_map = {"1": "sddm", "2": "gdm", "3": "lightdm", "4": "none"}
    selected_dm = dm_map.get(dm_choice, "sddm")
    config["display_manager"] = selected_dm

    # --- AUTO-BOOTSTRAP DISPLAY MANAGER ---
    if selected_dm != "none":
        print(f"\n[+] Auto-installing and enabling Display Manager: {selected_dm}...")
        subprocess.run(f"sudo pacman -S --needed --noconfirm {selected_dm}", shell=True)
        subprocess.run(f"sudo systemctl enable {selected_dm}", shell=True)

    # --- AUTO-BOOTSTRAP TERMINAL APP ---
    term = config.get("default_terminal", "konsole")
    subprocess.run(f"sudo pacman -S --needed --noconfirm {term}", shell=True)

    python_exec = os.path.expanduser("~/wswm/venv/bin/python3")
    script_path = os.path.abspath(__file__)
    session_type = "Wayland" if backend == "wayland" else "XSession"

    desktop_content = f"""[Desktop Entry]
Name=WSWM-AI ({backend.upper()})
Comment=WSWM-AI Modular Window Manager with Neural Integration
Exec={python_exec} {script_path}
Type={session_type}
"""
    os.makedirs("/tmp/wswm", exist_ok=True)
    with open("/tmp/wswm.desktop", "w") as f:
        f.write(desktop_content)
     
    subprocess.run("sudo mkdir -p /usr/share/xsessions /usr/share/wayland-sessions", shell=True)
    target_dir = "/usr/share/wayland-sessions" if backend == "wayland" else "/usr/share/xsessions"
    subprocess.run(f"sudo cp /tmp/wswm.desktop {target_dir}/wswm.desktop", shell=True)

    config["session_registered"] = True
    save_config(config)
    print("\n[+] WSWM-AI Desktop Session successfully registered. You may reboot or re-login.")

def launch_workspace(hw_profile, config):
    subprocess.run("xrandr --auto", shell=True)

    subprocess.run("""
        xsetroot -cursor_name left_ptr
        for id in $(xinput list | grep -iE 'touchpad|synaptics|elan|alps|pointer' | awk -F= '{print $2}' | awk '{print $1}'); do
            xinput set-prop "$id" 'libinput Tapping Enabled' 1 2>/dev/null
            xinput set-prop "$id" 'libinput Natural Scrolling Enabled' 1 2>/dev/null
            xinput set-prop "$id" 'libinput Tapping Drag Enabled' 1 2>/dev/null
            xinput set-prop "$id" 'libinput Disable While Typing Enabled' 1 2>/dev/null
            xinput set-prop "$id" 'libinput Scroll Method Enabled' 0 1 1 2>/dev/null
        done 2>/dev/null || true
    """, shell=True)
     
    subprocess.run("sudo systemctl start touchegg 2>/dev/null || true", shell=True)
    subprocess.run("sudo systemctl start tlp 2>/dev/null || true", shell=True)

    menu_path = os.path.expanduser("~/wswm/core/menu.sh")
    os.makedirs(os.path.dirname(menu_path), exist_ok=True)
     
    menu_content = r"""#!/bin/bash
clear
echo -e "\033[1;36m    /\     \033[1;35m╔═══════════════════════════════════════════╗\033[0m"
echo -e "\033[1;36m   /  \    \033[1;35m║\033[1;32m       WSWM-AI NEURAL CORE v3.8        \033[1;35m║\033[0m"
echo -e "\033[1;36m  /\   \   \033[1;35m╠═══════════════════════════════════════════╣\033[0m"
echo -e "\033[1;36m /       \  \033[1;33m * Architecture : \033[0mx86_64 Modular X11\033[1;35m ║\033[0m"
echo -e "\033[1;36m/   AI   \ \033[1;33m * Core Status  : \033[1;32mFully Synchronized\033[1;35m ║\033[0m"
echo -e "\033[1;36m/   [==]   \ \033[1;33m * Gestures     : \033[0mEnabled (1,2,3 Fingers)\033[1;35m║\033[0m"
echo -e "\033[1;36m/_--'   '--_\ \ \033[1;35m╚═══════════════════════════════════════════╝\033[0m"
echo "======================================================================"
echo -e "                    \033[1;32m[ WSWM WINDOW MANAGEMENT SUITE ]\033[0m"
echo "======================================================================"
echo " [1] Independent Terminal Session (Standard Bash Shell)"
echo " [2] Launch AI Terminal Agent (Gemini Neural Engine)"
echo " [3] Brave Browser Workspace Assistance"
echo "----------------------------------------------------------------------"
read -rp " Select workspace workflow option (1-3) [Default 1]: " opt
if [ "$opt" = "2" ]; then
    python3 ~/wswm/core/wswm.py --ai-mode
elif [ "$opt" = "3" ]; then
    exec bash
else
    exec bash
fi
"""
    with open(menu_path, "w", encoding="utf-8") as f:
        f.write(menu_content)
    subprocess.run(f"chmod +x {menu_path}", shell=True)
     
    term = config.get("default_terminal", "konsole")
    subprocess.Popen(f"{term} --noclose -e {menu_path} &", shell=True)
    time.sleep(1.8)
    subprocess.Popen("brave --no-sandbox &", shell=True)

    time.sleep(2.5)
    subprocess.run("""
        if command -v xdotool &> /dev/null; then
            read SCREEN_W SCREEN_H < <(xdpyinfo | awk '/dimensions/{print $2}' | tr 'x' ' ')
            
            if [ -z "$SCREEN_W" ] || [ -z "$SCREEN_H" ]; then
                read SCREEN_W SCREEN_H < <(xrandr | awk '/\*current/{print $1} {if ($1 ~ /^[0-9]+x[0-9]+$/) print $1}' | head -n 1 | tr 'x' ' ')
            fi
            
            SCREEN_W=${SCREEN_W:-1366}
            SCREEN_H=${SCREEN_H:-768}
            
            HALF_W=$((SCREEN_W / 2))
            
            TERM_ID=$(xdotool search --class "konsole" | head -n 1)
            BRAVE_ID=$(xdotool search --class "brave" | head -n 1)
            
            if [ ! -z "$BRAVE_ID" ]; then
                xdotool windowactivate "$BRAVE_ID"
                xdotool windowunmaximize "$BRAVE_ID" 2>/dev/null || true
                xdotool windowmove "$BRAVE_ID" 0 0
                xdotool windowsize "$BRAVE_ID" "$HALF_W" "$SCREEN_H"
            fi
            
            if [ ! -z "$TERM_ID" ]; then
                xdotool windowactivate "$TERM_ID"
                xdotool windowunmaximize "$TERM_ID" 2>/dev/null || true
                xdotool windowmove "$TERM_ID" "$HALF_W" 0
                xdotool windowsize "$TERM_ID" "$HALF_W" "$SCREEN_H"
            fi
            
            if command -v notify-send &> /dev/null; then
                notify-send "WSWM-AI Workspace" "Split screen: Brave (Kiri), Terminal (Kanan) & Touchpad Scroll aktif!" -u normal
            fi
        fi
    """, shell=True)

class ModularWindowManager:
    def __init__(self, backend="x11"):
        self.backend = backend.lower()

    def run(self):
        try:
            if self.backend == "wayland":
                while True:
                    time.sleep(1)
            else:
                from Xlib import display, X
                disp = display.Display()
                root = disp.screen().root
                root.change_attributes(event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask | X.MapRequestMask)
                disp.sync()
                while True:
                    event = disp.next_event()
                    if event.type == X.MapRequest:
                        event.window.map()
                        disp.sync()
        except Exception as e:
            print(f"[!] Modular Window Manager loop encountered an anomaly: {e}")
            while True:
                time.sleep(5)

def main():
    if "--ai-mode" in sys.argv:
        config = load_or_init_config()
        hw_profile = json.load(open(AUDIT_PATH)) if os.path.exists(AUDIT_PATH) else perform_audit()
        api_key = get_or_set_api_key(config)
        client = genai.Client(api_key=api_key)
        print("\n[+] WSWM-AI Neural Agent active. Type natural language commands or 'exit' to quit.\n")
        while True:
            try:
                q = input("WSWM-AI> ").strip()
                if not q:
                    continue
                if q in ["exit", "quit"]:
                    print("[*] Terminating AI agent session...")
                    break
                res = call_gemini(client, f"Translate the following user request into a safe, robust Arch Linux bash command block. Output only raw bash code: {q}")
                print(f"\nGenerated Command Payload:\n{res}\n" + "-"*40)
                if input("Execute payload? (y/n): ").strip().lower() == 'y':
                    execute_action(res)
            except (KeyboardInterrupt, EOFError):
                print("\n[!] Session interrupted.")
                break
        return

    config = load_or_init_config()
    is_session = not sys.stdin.isatty()

    if not is_session:
        api_key = get_or_set_api_key(config)
        client = genai.Client(api_key=api_key)
        hw_profile = perform_audit()
        setup_wizard(client, hw_profile, config)
        return
    else:
        hw_profile = json.load(open(AUDIT_PATH)) if os.path.exists(AUDIT_PATH) else perform_audit()
        launch_workspace(hw_profile, config)
        wm = ModularWindowManager(backend=config.get("display_server", "x11"))
        wm.run()

if __name__ == "__main__":
    main()
