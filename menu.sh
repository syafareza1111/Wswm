#!/bin/bash
clear
echo -e "\033[1;36m     /\       \033[1;35m╔═════════════════════════════════════════╗\033[0m"
echo -e "\033[1;36m    /  \      \033[1;35m║\033[1;32m       WSWM-AI NEURAL CORE v3.8      \033[1;35m║\033[0m"
echo -e "\033[1;36m   /\   \     \033[1;35m╠═════════════════════════════════════════╣\033[0m"
echo -e "\033[1;36m  /      \    \033[1;33m * Architecture : \033[0mx86_64 Modular X11\033[1;35m ║\033[0m"
echo -e "\033[1;36m /   AI   \   \033[1;33m * Core Status  : \033[1;32mFully Synchronized\033[1;35m ║\033[0m"
echo -e "\033[1;36m/   [==]   \  \033[1;33m * Gestures     : \033[0mEnabled (1,2,3 Fingers)\033[1;35m║\033[0m"
echo -e "\033[1;36m/_--'   '--_\ \ \033[1;35m╚═════════════════════════════════════════╝\033[0m"
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
