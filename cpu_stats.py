#!/usr/bin/env python3
import psutil
from typing import Tuple

try:
    import psutil
except ImportError:
    print("psutil not found. Install with: pip install psutil")
    exit(1)


def get_cpu_usage() -> float:
    """Get CPU usage percentage."""
    return psutil.cpu_percent(interval=0.1)


def get_ram_usage() -> Tuple[int, int, float]:
    """Get RAM usage in MB and total MB."""
    mem = psutil.virtual_memory()
    used_mb = mem.used // (1024 * 1024)
    total_mb = mem.total // (1024 * 1024)
    return used_mb, total_mb, mem.percent
