# Architecture

The monitoring system is modular.

Modules

gpu_stats.py
Collects GPU utilization and VRAM via nvidia-smi.

cpu_stats.py
Collects CPU and RAM usage via psutil.

llm_servers.py
Checks llama.cpp server endpoints.

comfyui.py
Checks ComfyUI server ports.

dashboard.py
Handles terminal rendering.

ai_monitor.py
Main loop orchestrating all modules.
