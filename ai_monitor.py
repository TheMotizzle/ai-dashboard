#!/usr/bin/env python3
import time
from gpu_stats import get_gpu_stats
from cpu_stats import get_cpu_usage, get_ram_usage
from power_stats import get_power_stats
from llm_servers import get_all_llm_server_status
from comfyui import get_all_comfyui_servers
from dashboard import Dashboard

LLM_SERVER_PORTS = [8181, 8182]
COMFYUI_SERVERS = [
    {"port": 8188, "label": "Work Mode"},
    {"port": 8189, "label": "Private Mode"}
]


def main():
    """Main loop."""
    dashboard = Dashboard()
    try:
        while True:
            gpus = get_gpu_stats()
            power_data = get_power_stats()
            cpu_usage = get_cpu_usage()
            ram_used, ram_total, ram_pct = get_ram_usage()
            llm_servers = get_all_llm_server_status(LLM_SERVER_PORTS)
            comfyui_ports = [s["port"] for s in COMFYUI_SERVERS]
            comfyui_servers = get_all_comfyui_servers(comfyui_ports)

            dashboard.update(gpus, cpu_usage, ram_used, ram_total, ram_pct,
                            llm_servers, comfyui_servers, COMFYUI_SERVERS, power_data)
            time.sleep(1)
    except KeyboardInterrupt:
        dashboard.console.print("\nMonitoring stopped.", style="bold")
    finally:
        dashboard.stop()


if __name__ == "__main__":
    main()
