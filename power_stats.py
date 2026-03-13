#!/usr/bin/env python3
import subprocess
from typing import Optional, Dict

# Risk thresholds based on power load percentage
POWER_LOW_MAX = 70
POWER_MODERATE_MAX = 90


def get_power_stats() -> Optional[Dict]:
    """Get power, thermal, and fan data from nvidia-smi."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=power.draw,power.limit,temperature.gpu,fan.speed",
                "--format=csv,noheader,nounits"
            ],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None

        parts = [p.strip() for p in result.stdout.strip().split(",")]
        if len(parts) < 4:
            return None

        power_draw = float(parts[0])
        power_limit = float(parts[1])
        gpu_temp = int(parts[2])
        fan_speed = int(parts[3])

        power_pct = (power_draw / power_limit * 100) if power_limit > 0 else 0
        risk = _calculate_risk(power_pct)

        return {
            "power_draw": power_draw,
            "power_limit": power_limit,
            "power_pct": power_pct,
            "gpu_temp": gpu_temp,
            "fan_speed": fan_speed,
            "risk_level": risk,
        }
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
        return None


def _calculate_risk(power_pct: float) -> str:
    if power_pct >= POWER_MODERATE_MAX:
        return "HIGH"
    elif power_pct >= POWER_LOW_MAX:
        return "MODERATE"
    return "LOW"
