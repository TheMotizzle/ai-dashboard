#!/usr/bin/env python3
import time
from gpu_stats import get_gpu_stats
from cpu_stats import get_cpu_usage, get_ram_usage
from llm_servers import get_all_llm_server_status
from comfyui import get_all_comfyui_servers
from dashboard import display_stats

LLM_SERVER_PORTS = [8181, 8182]
COMFYUI_SERVERS = [
    {"port": 8188, "label": "Work Mode"},
    {"port": 8189, "label": "Private Mode"}
]


def main():
    """Main loop."""
    try:
        while True:
            gpus = get_gpu_stats()
            cpu_usage = get_cpu_usage()
            ram_used, ram_total, ram_pct = get_ram_usage()
            llm_servers = get_all_llm_server_status(LLM_SERVER_PORTS)
            comfyui_ports = [s["port"] for s in COMFYUI_SERVERS]
            comfyui_servers = get_all_comfyui_servers(comfyui_ports)
            
            display_stats(gpus, cpu_usage, ram_used, ram_total, ram_pct, llm_servers, comfyui_servers, COMFYUI_SERVERS)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
