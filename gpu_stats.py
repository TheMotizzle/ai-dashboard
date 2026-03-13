#!/usr/bin/env python3
import subprocess
from typing import Optional, List, Dict


def get_gpu_stats() -> Optional[List[Dict]]:
    """Get GPU utilization and VRAM usage from nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        
        gpus: List[Dict] = []
        lines = result.stdout.strip().split("\n")
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 3:
                util = int(parts[0].strip())
                used = int(parts[1].strip())
                total = int(parts[2].strip())
                vram_pct = (used / total * 100) if total > 0 else 0
                used_gb = used / 1024
                total_gb = total / 1024
                gpus.append({
                    "utilization": util,
                    "vram_used_gb": used_gb,
                    "vram_total_gb": total_gb,
                    "vram_pct": vram_pct
                })
        return gpus if gpus else None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None
