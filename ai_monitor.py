#!/usr/bin/env python3
import json
import socket
import subprocess
import time
from typing import Optional, List, Dict
import urllib.request

try:
    import psutil
except ImportError:
    print("psutil not found. Install with: pip install psutil")
    exit(1)


LLM_SERVER_PORTS = [8181, 8182]
HTTP_TIMEOUT = 2


def get_gpu_stats() -> tuple[Optional[str], Optional[str]]:
    """Get GPU utilization and VRAM usage from nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None, None
        
        lines = result.stdout.strip().split("\n")
        utils_and_vrams = []
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 3:
                util = int(parts[0].strip())
                used = int(parts[1].strip())
                total = int(parts[2].strip())
                pct = (used / total * 100) if total > 0 else 0
                used_gb = used / 1024
                total_gb = total / 1024
                vram_str = f"{used_gb:.1f}/{total_gb:.1f} GB ({pct:.1f}%)"
                utils_and_vrams.append((util, vram_str))
        
        return (", ".join(f"GPU{i}: {u[0]}%" for i, u in enumerate(utils_and_vrams)),
                ", ".join(f"GPU{i}: {v[1]}" for i, v in enumerate(utils_and_vrams)))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None, None


def get_cpu_usage() -> float:
    """Get CPU usage percentage."""
    return psutil.cpu_percent(interval=0.1)


def get_ram_usage() -> tuple[int, int, float]:
    """Get RAM usage in MB and total MB."""
    mem = psutil.virtual_memory()
    used_mb = mem.used // (1024 * 1024)
    total_mb = mem.total // (1024 * 1024)
    return used_mb, total_mb, mem.percent


def format_bar(value: float, max_value: int = 100) -> str:
    """Create a progress bar."""
    filled = int((value / max_value) * 20)
    empty = 20 - filled
    return "█" * filled + "░" * empty


def get_llm_server_status(port: int) -> Dict:
    """Check LLM server status on given port."""
    result = {
        "port": port,
        "status": "OFFLINE",
        "model_id": None
    }
    
    try:
        url = f"http://localhost:{port}/v1/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            result["status"] = "ONLINE"
            if isinstance(data.get("data"), list) and len(data["data"]) > 0:
                result["model_id"] = data["data"][0].get("id", "unknown")
    except Exception:
        pass
    
    return result


def display_stats():
    """Display all system stats in a formatted table."""
    
    gpu_util, gpu_vram = get_gpu_stats()
    cpu_usage = get_cpu_usage()
    ram_used, ram_total, ram_pct = get_ram_usage()
    llm_servers = [get_llm_server_status(port) for port in LLM_SERVER_PORTS]
    
    print("\033[H\033[J", end="")
    
    timestamp = time.strftime("%H:%M:%S")
    
    print(f" " + "═" * 48)
    print(f" AI System Monitor - {timestamp}")
    print(f" " + "═" * 48)
    
    print("\n📊 GPU STATUS")
    print("-" * 25)
    if gpu_util:
        print(f"  Utilization: {gpu_util}")
        print(f"  VRAM Usage:  {gpu_vram}")
    else:
        print("  No NVIDIA GPU detected")
        print("  (or nvidia-smi not available)")
    
    print("\n💻 CPU USAGE")
    print("-" * 25)
    bar = format_bar(cpu_usage)
    print(f"  [{bar}] {cpu_usage:.1f}%")
    
    print("\n📦 RAM USAGE")
    print("-" * 25)
    bar = format_bar(ram_pct)
    print(f"  [{bar}] {ram_pct:.1f}% ({ram_used} / {ram_total} MB)")
    
    print("\n🤖 LOCAL LLM SERVERS")
    print("-" * 25)
    for server in llm_servers:
        status_icon = "●" if server["status"] == "ONLINE" else "○"
        model_display = server.get("model_id") or "N/A"
        print(f"  Port {server['port']}: {status_icon} {server['status']} - {model_display}")
    
    print("\n " + "═" * 48)
    print(" Refreshing every second... Press Ctrl+C to exit")
    print(" " + "═" * 48)


def main():
    """Main loop."""
    try:
        while True:
            display_stats()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
