#!/usr/bin/env python3
"""Dashboard module for displaying system stats."""
import time
from typing import List, Dict, Tuple, Optional


def format_bar(value: float, max_value: int = 100) -> str:
    """Create a progress bar."""
    filled = int((value / max_value) * 24)
    empty = 24 - filled
    return "█" * filled + "░" * empty


def display_stats(
    gpu_data: Optional[List[Dict]],
    cpu_usage: float,
    ram_used: int,
    ram_total: int,
    ram_pct: float,
    llm_servers: List[Dict],
    comfyui_servers: List[Dict],
    comfyui_labels: List[Dict]
) -> None:
    """Display all system stats in a formatted table."""
    print("\033[H\033[J", end="")
    
    timestamp = time.strftime("%H:%M:%S")
    
    print(f" " + "═" * 48)
    print(f" AI System Monitor - {timestamp}")
    print(f" " + "═" * 48)
    
    print("\n📊 GPU STATUS")
    print("-" * 25)
    if gpu_data:
        for i, gpu in enumerate(gpu_data):
            if i > 0:
                print()
            util_bar = format_bar(gpu["utilization"])
            vram_bar = format_bar(gpu["vram_pct"])
            print(f"  GPU{i} Utilization")
            print(f"  [{util_bar}] {gpu['utilization']}%")
            print()
            print(f"  GPU{i} VRAM")
            print(f"  [{vram_bar}] {gpu['vram_used_gb']:.1f} / {gpu['vram_total_gb']:.1f} GB ({gpu['vram_pct']:.1f}%)")
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
    
    print("\n🎨 COMFYUI SERVERS")
    print("-" * 25)
    for i, server in enumerate(comfyui_servers):
        status_icon = "●" if server["status"] == "ONLINE" else "○"
        label = comfyui_labels[i]["label"] if i < len(comfyui_labels) else f"Port {server['port']}"
        print(f"  {label} ({server['port']}): {status_icon} {server['status']}")
    
    print("\n " + "═" * 48)
    print(" Refreshing every second... Press Ctrl+C to exit")
    print(" " + "═" * 48)
